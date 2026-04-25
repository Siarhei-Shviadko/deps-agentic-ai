from http import HTTPStatus
from uuid import uuid4

import pytest

from deps_agentic_ai.constants import V1_API_PREFIX


@pytest.mark.asyncio
async def test_create_mode__created(client, unit_of_work, test_tool_set_1, test_tool_set_2, add_tool_sets):
    code = "m1"
    tool_set_ids = [test_tool_set_1.id(), test_tool_set_2.id()]

    response = await client.post(
        f"{V1_API_PREFIX}/modes",
        json={
            "code": code,
            "toolSetIds": tool_set_ids,
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    mode_id = response.json().get("id")

    assert mode_id

    mode = await unit_of_work.modes.mode_of_id(mode_id)

    assert mode
    assert mode.code == code
    assert len(mode.tool_sets) == len(tool_set_ids)


@pytest.mark.asyncio
async def test_create_mode__already_exists(
    client,
    test_mode_1,
    test_tool_set_1,
    test_tool_set_2,
    add_modes,
    add_tool_sets,
):
    code = test_mode_1.code
    tool_set_ids = [test_tool_set_1.id(), test_tool_set_2.id()]

    response = await client.post(
        f"{V1_API_PREFIX}/modes",
        json={
            "code": code,
            "toolSetIds": tool_set_ids,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_create_mode__tool_sets_not_found(
    client,
    test_tool_set_1,
    test_tool_set_2,
    add_tool_sets,
):
    code = "m1"
    tool_set_ids = [test_tool_set_1.id(), test_tool_set_2.id(), uuid4().hex]

    response = await client.post(
        f"{V1_API_PREFIX}/modes",
        json={
            "code": code,
            "toolSetIds": tool_set_ids,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_modes__deleted(client, unit_of_work, test_mode_1, test_mode_3, add_modes):
    ids = {test_mode_1.id(), test_mode_3.id()}

    assert len(await unit_of_work.modes.modes_of_ids(ids)) == len(ids)

    response = await client.delete(
        f"{V1_API_PREFIX}/modes?id={test_mode_1.id()}&id={test_mode_3.id()}",
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not await unit_of_work.modes.modes_of_ids(ids)


@pytest.mark.asyncio
async def test_get_modes__ok(client, test_modes, add_modes, add_tool_sets):
    response = await client.get(f"{V1_API_PREFIX}/modes")

    assert response.status_code == HTTPStatus.OK

    modes_info = response.json()["modes"]

    assert len(modes_info) == len(test_modes)

    modes_info = sorted(modes_info, key=lambda m: m["code"])
    modes = sorted(test_modes, key=lambda m: m.code)

    for mode_info, mode in zip(modes_info, modes):
        tool_sets_info = sorted(mode_info["toolSets"], key=lambda ts: ts["name"])
        tool_sets = sorted(mode.tool_sets.values(), key=lambda ts: ts.name)

        for tool_set_info, tool_set in zip(tool_sets_info, tool_sets):
            assert tool_set_info["id"] == tool_set.id()
            assert tool_set_info["code"] == tool_set.code
            assert tool_set_info["name"] == tool_set.name
            assert len(tool_set_info["tools"]) == len(tool_set.tools)

            for tool_info, tool in zip(tool_set_info["tools"], tool_set.tools):
                assert tool_info["code"] == tool.code
                assert tool_info["name"] == tool.name
                assert len(tool_info["parameters"]) == len(tool.parameters)

                for parameter_info, parameter in zip(tool_info["parameters"], tool.parameters):
                    assert parameter_info["name"] == parameter.name


@pytest.mark.asyncio
async def test_get_modes__with_code__ok(client, test_mode_1, test_modes, add_modes, add_tool_sets):
    response = await client.get(f"{V1_API_PREFIX}/modes?code={test_mode_1.code}")

    assert response.status_code == HTTPStatus.OK

    modes_info = response.json()["modes"]

    assert len(modes_info) == 1

    mode_info = modes_info[0]

    assert mode_info["id"] == test_mode_1.id()
    assert mode_info["code"] == test_mode_1.code


@pytest.mark.asyncio
async def test_get_modes__with_code__no_modes(client, test_mode_1, test_modes, add_modes, add_tool_sets):
    response = await client.get(f"{V1_API_PREFIX}/modes?code={uuid4().hex}")

    assert response.status_code == HTTPStatus.OK

    modes_info = response.json()["modes"]

    assert len(modes_info) == 0


@pytest.mark.asyncio
async def test_update_mode_code__updated(client, unit_of_work, test_mode_1, add_modes, add_tool_sets):
    code = "test"

    response = await client.patch(
        f"{V1_API_PREFIX}/modes/{test_mode_1.id()}/code",
        json={
            "code": code,
        },
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    mode = await unit_of_work.modes.mode_of_id(test_mode_1.id())

    assert mode.code == code


@pytest.mark.asyncio
async def test_update_mode_code__mode_not_found(client, test_mode_1):
    code = "test"

    response = await client.patch(
        f"{V1_API_PREFIX}/modes/{test_mode_1.id()}/code",
        json={
            "code": code,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_mode_code__mode_with_code_already_exists(client, test_mode_1, test_mode_2, add_modes):
    code = test_mode_2.code

    response = await client.patch(
        f"{V1_API_PREFIX}/modes/{test_mode_1.id()}/code",
        json={
            "code": code,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_update_mode_tool_sets__updated(
    client,
    unit_of_work,
    test_mode_1,
    test_tool_set_1,
    test_tool_set_2,
    test_tool_set_3,
    add_modes,
    add_tool_sets,
):
    to_add = [test_tool_set_3.id()]
    to_remove = [test_tool_set_2.id(), test_tool_set_1.id()]

    response = await client.patch(
        f"{V1_API_PREFIX}/modes/{test_mode_1.id()}/tool-sets",
        json={
            "addIds": to_add,
            "removeIds": to_remove,
        },
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    mode = await unit_of_work.modes.mode_of_id(test_mode_1.id())

    assert mode.tool_set_ids == {test_tool_set_3.id()}


@pytest.mark.asyncio
async def test_update_mode_tool_sets__tool_sets_not_found(
    client,
    test_mode_1,
    test_tool_set_1,
    test_tool_set_2,
    test_tool_set_3,
    add_modes,
):
    to_add = [test_tool_set_3.id()]
    to_remove = [test_tool_set_2.id(), test_tool_set_1.id()]

    response = await client.patch(
        f"{V1_API_PREFIX}/modes/{test_mode_1.id()}/tool-sets",
        json={
            "addIds": to_add,
            "removeIds": to_remove,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
