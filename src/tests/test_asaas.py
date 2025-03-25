# import random

# import pytest
# from loguru import logger

# from modules import asaas


# @pytest.mark.asyncio
# async def test_asaas_create_payment_link():
#     api_response = await asaas.api_create_payment_link(
#         externalReference=f'teste_{random.randint(9999, 10000)}',
#         name='Pagamento Teste',
#         value=5.00,
#         callback_url='https://caderninho.up.railway.app/',
#         description='Descrição teste',
#         auto_redirect=False
#     )
#     logger.info(api_response)
#     logger.info(api_response.url)
#     assert api_response.url
