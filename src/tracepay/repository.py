"""Read-only repository for synthetic evidence fixtures."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


class FixtureError(ValueError):
    pass


class FixtureRepository:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.data_dir = (self.project_root / "data" / "synthetic").resolve()
        self.manifest_path = self.project_root / "evaluation" / "cases" / "manifest.json"

    def _manifest(self) -> Dict[str, Any]:
        with self.manifest_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def case_definitions(self) -> List[Dict[str, Any]]:
        return self._manifest()["cases"]

    def dataset_frozen_at(self) -> str:
        """Return the declared synthetic evidence snapshot timestamp."""
        value = self._manifest().get("frozen_at")
        if not isinstance(value, str):
            raise FixtureError("Manifest frozen_at is missing")
        return value

    def case_definition(self, case_id: str) -> Dict[str, Any]:
        matches = [case for case in self.case_definitions() if case["case_id"] == case_id]
        if not matches:
            raise FixtureError("Unknown case_id: %s" % case_id)
        return matches[0]

    def fixture_path(self, case_id: str) -> Path:
        definition = self.case_definition(case_id)
        path = (self.data_dir / definition["fixture"]).resolve()
        if path.parent != self.data_dir:
            raise FixtureError("Fixture path escapes data directory")
        return path

    def load_case(self, case_id: str) -> Dict[str, Any]:
        path = self.fixture_path(case_id)
        with path.open("r", encoding="utf-8") as handle:
            case = json.load(handle)
        if case.get("case_id") != case_id:
            raise FixtureError("Case ID does not match fixture: %s" % path)
        return case

    def integrity(self, case_id: str) -> str:
        raw = self.fixture_path(case_id).read_bytes()
        return "sha256:%s" % hashlib.sha256(raw).hexdigest()
