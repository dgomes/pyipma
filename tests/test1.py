import asyncio
import pytest
from pyipma import Agent 

def test_retrive_pda_page():

    async def retrieve_page():
        agent = Agent("Aveiro")
        r = await agent._get(url="http://pda.ipma.pt/observacao.jsp")
        assert 7000 < len(r) < 9000 

    loop = asyncio.get_event_loop()
    loop.run_until_complete(retrieve_page())

def test_aveiro():

    agent = Agent("Aveiro")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(agent.retrieve_station("Aveiro"))

    assert False
