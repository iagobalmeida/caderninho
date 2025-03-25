import pytest

from domain import repository


@pytest.mark.asyncio
async def test_cache():
    await repository.set_cache('a', 'b', 'c', value='foo')
    cached = await repository.get_cache('a', 'b', 'c')
    assert cached['value'] == 'foo'
    await repository.unset_cache('a', 'b', 'c')
    cached = await repository.get_cache('a', 'b', 'c')
    assert cached == None
