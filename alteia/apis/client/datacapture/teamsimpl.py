from typing import List, overload

from alteia.apis.provider import AssetManagementAPI
from alteia.core.resources.resource import Resource
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class TeamsImpl:
    def __init__(self, asset_management_api: AssetManagementAPI, **kwargs):
        self._provider = asset_management_api

    def create(self, *, company: ResourceId, name: str, leader: ResourceId | None = None, **kwargs) -> Resource:
        """Create a team.

        Args:
            company: Identifier of the company.

            name: Team name.

            leader: Optional team leader (pilot id).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A team resource.
        """
        data = kwargs
        data.update(
            {
                "name": name,
                "company": company,
            }
        )

        if leader is not None:
            data["leader"] = leader

        content = self._provider.post(path="create-team", data=data)

        return Resource(**content)

    def search(
        self,
        *,
        filter: dict | None = None,
        limit: int | None = None,
        page: int | None = None,
        sort: dict | None = None,
        **kwargs,
    ) -> List[Resource]:
        """Search teams.

        Args:
            filter: Search filter dictionary.

            limit: Maximum number of results to extract.

            page: Page number (starting at page 0).

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resources: A list of team resources.

        """

        data = kwargs

        for name, value in [
            ("filter", filter or {}),
            ("limit", limit),
            ("page", page),
            ("sort", sort),
        ]:
            if value is not None:
                data.update({name: value})

        r = self._provider.post("search-teams", data=data)
        results = r.get("results")

        return [Resource(**m) for m in results]

    @overload
    def describe(self, team: ResourceId, **kwargs) -> Resource: ...

    @overload
    def describe(self, team: List[ResourceId], **kwargs) -> List[Resource]: ...

    def describe(self, team: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a team or list of teams.

        Args:
            team: Identifier of the team to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A team resource or a list of team resources.

        """
        data = kwargs
        if isinstance(team, list):
            results = []
            ids_chunks = get_chunks(team, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data["teams"] = ids_chunk
                descs = self._provider.post("describe-teams", data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data["team"] = team
            desc = self._provider.post("describe-team", data=data)
            return Resource(**desc)

    def delete(self, team: ResourceId, **kwargs) -> None:
        """Delete a team.

        Args:
            team: Identifier of the team to delete.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.
        """

        data = kwargs
        data["team"] = team

        self._provider.post("delete-team", data=data)

    def set_leader(self, team: ResourceId, *, leader: ResourceId, **kwargs) -> Resource:
        """Set the team leader.

        Args:
            team: Identifier of the team.

            leader: Identifier of the pilot to promote to leader.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The updated team resource.

        """

        data = kwargs
        data["team"] = team
        data["leader"] = leader

        desc = self._provider.post("set-team-leader", data=data)
        return Resource(**desc)

    def rename(self, team: ResourceId, name: str, **kwargs) -> Resource:
        """Rename a team.

        Args:
            team: Identifier of the team.

            name: New name.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The updated team resource.

        """

        data = kwargs
        data["team"] = team
        data["name"] = name

        desc = self._provider.post("set-team-name", data=data)
        return Resource(**desc)
