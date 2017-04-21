import logging
import threading
import json
import uuid
import platform
import Queue

from coapthon.resources.resource import Resource
from coapthon.server.coap import CoAP
from coapthon.client.helperclient import HelperClient
import socket
from coapthon import defines

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpclient
import tornado.websocket
import os

logger = logging.getLogger(__name__)


class ObservableResource(Resource):

    def __init__(self, name="Obs", coap_server=None, info={}):
        super(ObservableResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)

        self.info = info
        self.payload = json.dumps(self.info)
        self.period = 30
        self.update(True)

    def render_GET(self, request):
        return self

    def render_POST(self, request):
        self.payload = request.payload
        return self

    def update(self, first=False):
        self.payload = json.dumps(self.info)
        if not self._coap_server.stopped.isSet():

            if not first and self._coap_server is not None:
                logger.debug("Periodic Update")
                self._coap_server.notify(self)
                self.observe_count += 1


class CoAPServerPlugTest(CoAP):
    def __init__(self, host, port, multicast=False, starting_mid=None):
        CoAP.__init__(self, (host, port), multicast, starting_mid)

        # create logger
        logger.setLevel(logging.INFO)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)
        self.reslist = {}
        self.obs = {}

    def add_resources(self, res=[]):
        for r in res:
            self.reslist[r.info['id']] = r.info
            o = ObservableResource(coap_server=self, info=r.info)
            self.obs[r.info['id']] = o
            self.add_resource(r.path, o)


class MyResource(object):
    def __init__(self):
        self.path = None
        self.info = None

g_num = 0
uuid_cache=[  "0b190129-9e4c-4d2c-81e8-8573a56df071",
    "c313fcae-c5b4-4fa9-8024-89cb5c17aa90",
    "06075adc-4ec9-4dc3-ba12-729235653450",
    "495b208a-a77b-4115-a230-dcb28bf22b24",
    "ee7ec341-9500-4519-aa3b-bb522adc1e73",
    "795380e3-25b8-47a3-95db-b119cc32cc8d",
    "6b527de4-22de-4392-bc47-575a1134e17f",
    "8117a6ff-cf0e-4924-8bd1-033428aea692",
    "739d0d78-ca60-4832-ba35-b2b8ce0ee372",
    "7014edc0-2aa3-4bab-9b9f-a8361f51e42d",
    "1d7fa5b7-1af7-40b4-90e0-b736122c101d",
    "87b456ae-9fc8-4f3f-8446-b070224b975d",
    "5d58f4d3-b690-48bf-ab17-998f5b28d0c7",
    "dec9f808-47f8-4ed9-9f12-39bd5478b8d6",
    "a9a18d01-9c3a-4449-b1ca-23a20d507cdb",
    "bc02cec8-b0fe-49cc-93dc-2457f9b9c361",
    "05d28db3-0078-4297-8665-0d1c862b31dd",
    "24a55084-7fb5-418c-91d5-370e7e58e089",
    "2e78fe9d-117e-4b34-8c43-5cb51d743cec",
    "338e4457-8b83-407b-8b39-e4066e9f2396",
    "85342626-a160-43bf-9f1f-f1a44c608640",
    "b0bb6a1b-315b-4d9e-ae95-7bd8c32dd015",
    "34af1eed-9c77-48d9-ba9d-c1a8e79ee937",
    "61fa63be-2d1a-470b-9a49-28a367880b87",
    "8dd6631f-af09-4947-8cb7-fd53b2ce1b39",
    "9b4f00ec-1cfd-432e-8be7-6cb9c4f374be",
    "43887b5f-7852-4f69-963c-85be4819032a",
    "260ff310-506f-4f69-b758-8e3df90db2e1",
    "87b9e874-fbdd-4824-bcd0-90f4d1dd8689",
    "696dbddf-cd0f-4970-aa22-14ad8acda133",
    "41bdc3d1-a2b7-44f2-b751-41af2a07347f",
    "40062186-8902-4784-afd0-6088433a4ad0",
    "69f80c2a-7476-48e4-92ec-e2ba47f36f9e",
    "dd5dddd2-03f1-4de3-83f0-e547e355e37f",
    "de6e7992-9a13-406e-99b5-b758af0375a4",
    "2954f7a5-f449-4348-ab49-6f96f0705e80",
    "ba0a6830-dabf-40af-b634-b24416329ec4",
    "c936ad1a-d58c-4260-9499-81fdc105511f",
    "9423b08c-70c0-44a6-9eef-8e5f8a0099c1",
    "67239b6b-275b-4b55-a1b3-cddac0d3b5f3",
    "733f3948-7131-4311-98b9-57d792e51544",
    "1375f53c-cd76-4c93-a5bb-ca10a98a250b",
    "01ccdf5b-a8a0-4f09-82c1-918beee05544",
    "332442eb-a5dc-44ff-8d6b-eae96b31a85c",
    "bbdfb403-06e6-41b5-8a57-df8d9a7153b9",
    "cebf32d8-7152-422c-b611-98f645dd0631",
    "7033fa99-4431-4e5d-b0c7-cbe7a3fda7f7",
    "23d6dccb-1a5f-42e6-bbf7-1657a48ac9f7",
    "1ac1cb1a-1d02-4e7a-9ac0-3d0bd9a55901",
    "b2225973-b32b-4f91-8fac-8b48e02af486",
    "6b20afe0-cdb1-499e-844f-0041989ced5f",
    "17b26fbe-2023-4698-9c01-116fd2011f26",
    "c2953ffa-b5ef-476c-9979-5d69fc726c8b",
    "6383b5de-7cbf-4a5f-886c-662c1a3ce32c",
    "f1708f55-3022-425c-8074-acdfb88f6c3e",
    "fa7749bd-78a1-4b5c-ad87-f99a59b966d9",
    "c5e482dc-a40b-47e3-97e0-40ae828baf61",
    "9e9421b9-8efb-4a7a-aacc-4738b70f5122",
    "5a65499d-410e-46d0-89ec-5e6867993c2d",
    "035427a4-aece-4845-a533-00a54f604920",
    "0d18e897-f8ab-4d5b-9a70-1e8079dfab99",
    "21649df5-1ddc-4658-b510-8d5e73e65e59",
    "7e417509-09db-4e50-8528-5813f2fffe50",
    "aaf50478-4749-4a8b-9b92-f33569d6f02a",
    "1f4ea8d8-2a17-41ed-8be7-c1d53c9f8a7c",
    "157175df-68d6-4ff0-acbb-d75430fcb763",
    "4aef191e-5b64-4035-abfd-c2e156786d4b",
    "fd69b92c-5388-42a8-a448-5c176f26c1e5",
    "3c26d58f-8c00-4fef-8fab-5076ad341e53",
    "5b715470-eee5-4287-8795-9eace8ae793e",
    "c0dfb823-a38e-471c-a691-15d8ca6dfc29",
    "a88b1856-d221-4044-bb2a-4348157c6574",
    "19b9572d-9f91-4aa8-bc01-9a34208f88e1",
    "9558e37d-1c48-4537-b804-a0e9eb8f7ef9",
    "159117ce-89db-441c-8291-9710212b6714",
    "290879e0-9a46-4954-aac1-ac902f6270de",
    "bfd15abe-802f-4c52-99d7-305278968cb1",
    "2faa741a-339a-47f2-8047-541b82cf67df",
    "c40c7b3c-a67f-43ae-be7e-32aad6006225",
    "980e6fa4-8fa2-4f72-b2bf-2e228c1a3ba0",
    "12017a1b-27cd-429c-84c7-3640edba78bd",
    "d0b7656d-e83e-42b9-9724-a05382dd911d",
    "e6800292-474c-42b9-bcc6-71a95e7db810",
    "cf8f095b-3a15-4d26-8dae-13bc6fae1137",
    "33c4e480-3b32-45dd-91d5-4e92fc2d5645",
    "3d66a9ea-37b4-4833-8220-e669a74d464b",
    "aa9c3f53-a0f8-48f2-822b-02f00fa749ca",
    "c0fc06b0-10f4-45e5-95fa-8529f7af094e",
    "3b173f85-7802-4222-b056-957603492dfc",
    "2451f5cf-8fca-4244-84fa-1da4886480ee",
    "48c44b80-5ac0-488c-8214-8a1515d2a714",
    "d937af47-a246-44ce-901e-654077803ec7",
    "813d6450-a34e-4a5e-a23d-84b5d9a1e095",
    "04028cef-90be-45c2-b9f8-0793c9c4752d",
    "e00ca1c0-9f52-416e-856b-2d10a398239a",
    "25b9bf37-d235-4cd1-bd91-236939814ead",
    "5d8f3117-c2dc-469a-ba59-514a909519f9",
    "ccc4e485-e076-46cf-aead-3882d3220e43",
    "f0b63cb8-d794-4705-8eaf-eeb871e40ae8",
    "7e52beda-0481-4acf-b49d-532577bc5e56",
    "5c423b81-c3c2-46ff-a85b-ad956364068a",
    "35bd9d2a-a461-4625-87c9-7e5a694a87cb",
    "3f51d81a-ce15-4bbc-a8dd-7474e1706980",
    "8a3ee8c8-7eac-44d9-9f59-dc6cf79ad54b",
    "a353e2b6-b836-45f5-a806-6f6ad2460d34",
    "cb591fa1-2340-498b-bebf-19de8de8d552",
    "e18f7c2c-0885-440f-883e-915d3b4684b5",
    "c47e4993-51bc-4507-b728-cf41bf1711e0",
    "2bb5bf75-1bb8-43fc-ae60-e5cc120b4b41",
    "964f35df-bb12-4e79-85f1-d37a378a1343",
    "40ac07da-429c-4b5c-858b-1b7f18e7eb1d",
    "30d2a882-b9aa-4cf7-ab59-69fc036d28c4",
    "d8532fb9-0627-4038-94d5-d5c376a8ab3c",
    "cf4e14ba-a844-43e6-b2e3-cba2e68d79bb",
    "83623529-ded5-4334-a848-8713184eb3b4",
    "311e1c80-eb26-490d-ac8f-90dfbca67f3f",
    "36c58dd6-c92a-448e-a5f9-503fcdeda734",
    "3a58495f-bed5-4aeb-87ec-0606230366db",
    "139f2267-ea97-48c2-9752-10218610adc8",
    "84482441-fad9-4bc9-9cb8-87b9baff9bca",
    "d1c89eec-395a-4f4f-b8a1-cd8512c780f4",
    "b22a64f6-9f5a-431e-94cf-26e1f63ece55",
    "94819501-f1e4-40bb-a457-0b92b1bda3c4",
    "e8c28b85-34a6-4919-9a80-8610d5a4bbcf",
    "6acb667b-e710-490c-8044-b93d31e40ca1",
    "c1861cd5-d0a1-4cff-92fe-1a31d7c13f80",
    "6fd9e269-ceb3-43c5-beb5-b6cd72dce85e",
    "849e24e8-1a42-495b-87e9-cbdc6196f8bf",
    "41c0503e-f685-4a97-84d9-1cc06dbceb91",
    "199cbbbe-4382-4d75-af02-3c028dab673b",
    "d6211861-c0dc-4c67-bcb3-3103105165ca",
    "c7713464-a4c1-40d9-bcc4-666e0f9da71e",
    "82964b82-ca6a-4356-8e8e-75e98e63bd6b",
    "cc4530d4-3019-4b8c-a485-c8e68453ed18",
    "dc38c661-56d8-44c3-b639-253fe78c3385",
    "3a2e3e38-894f-4e10-bde9-f64766940144",
    "1ea7be79-c282-4887-b8b5-a77cc405f7a5",
    "7565a0a8-9c4b-41e9-acae-876d548fdac7",
    "24dfa71c-595d-46a1-95c1-c2c03847d0b9",
    "65c5ae80-6e6f-495e-b761-7c50eac40cb6",
    "a56c6b93-d015-4908-b5af-023d928c8b98",
    "d9cec86b-76d7-4be6-9561-bae84418ba8c",
    "088b9941-16a0-4bcf-8ff1-2134e183b4fb",
    "75987712-6587-4cbd-b1d2-4ab9af3c7739",
    "b9d1eb0e-0cf2-4d04-8abd-b80f873a8f09",
    "38a2ffff-4bdd-4a80-88b0-a9bdfb2c8506",
    "3234cb84-a3c8-4ffc-8545-629e900e3129",
    "0393397f-159f-4ad8-8cd8-1f9b5521c621",
    "865f9e21-e319-4e35-b782-d029fb433076",
    "dacc4ebd-0e31-456b-bffb-97882024af81",
    "565523b4-7965-406f-89fc-2a32b136d66d",
    "ad196460-ffc4-45cc-93c5-99f1c130e84a",
    "ff9fe183-7c66-447f-87cc-ddafe13cfba3",
    "8fe13186-0a7e-44b5-afb3-0a69fdb867b1",
    "f160f189-a9eb-4999-ab9c-5d3242bdb4d6",
    "1623ead6-424c-4b4c-ba42-9d155886618e",
    "591d86ce-6140-43fb-b3d4-10c381bdf5fe",
    "82d4610a-aa9d-4364-a7bb-ae1bf486f84e",
    "56dd3857-53ec-4531-8d32-c5d87a4dd412",
    "4fe433f3-12d5-42c8-82b1-7d281fbacd33",
    "814f0f96-060c-4e3e-a3f1-59b16fef6c9f",
    "cff7f4b5-6ab8-46c3-89e0-f5ab379094bc",
    "46748663-3950-46d9-92fb-b45acb9f6677",
    "b762a386-2712-4159-b9b8-59c4c37dbdad",
    "2ad85c6e-a4fb-4d10-bf40-d1c6c9a1d538",
    "2dce9c59-1bb8-4bbf-8edc-28bc983833c1",
    "0d78d530-8563-4033-a9f5-33165871cc56",
    "0cb5c398-65b2-4c0f-abce-7cce50e994fa",
    "015f9f1f-2c39-44c5-89cd-638970dc6ba8",
    "5de2a47f-fe8d-4246-ad13-635d8972b7ba",
    "17050a8d-cbdd-4ce8-bea5-f570a7f92bbc",
    "8e086b05-19f5-4069-94e7-9cbbd9e532a9",
    "b58e57fa-f9e2-426e-a88a-252c69f04712",
    "9a88d41d-686a-4195-a22c-323c323512c6",
    "d58ab903-f651-405f-93f2-ab3285d96b3a",
    "d740ec28-e8c4-4409-97c5-67477d9423c5",
    "fa311fdd-4782-42f6-b481-a58e0d4f8783",
    "efc088aa-8248-4203-aa8b-804aedb6b3c0",
    "77ab0e77-8a5b-417b-900a-fd2d1ae08e0a",
    "12752d1c-afe7-4194-be03-74feab9a8c1c",
    "418d79a1-de83-41ad-a5ad-3bcff398c9e7",
    "121f9ba0-1a88-470f-b283-980588be2ac8",
    "0d483852-bff4-439b-8b55-a262a78edac1",
    "90a33170-688a-4999-8d80-a42a732e013e",
    "b19645f6-53a7-4102-90a4-a51274ff7d35",
    "c2ee8a62-3229-42b0-bf12-b372151e6ab6",
    "70252786-67c4-42e8-9b62-aec66877ad61",
    "b4c7bf27-bde4-4e6e-835d-279ccec96d59",
    "1d0a7e9b-7ed6-47ba-aa4f-3118d6636444",
    "9abd6bd4-204b-4736-89f5-967d422da8c8",
    "75a31dfe-89e0-4c08-b507-eea62473a75d",
    "f425a57a-270c-475d-b24c-fc00e3fe6d8c",
    "c145fd55-ed6a-4a09-9b43-acb8d46dde96",
    "ae237ca8-eaa3-4148-98cd-47f5c36a4f65",
    "48aec7e4-17a6-4c05-a62f-8acd2e1983ce",
    "21e7fb64-4c00-4437-91c2-3a863658ff71",
    "98ebd7e3-1589-4de7-bc75-92c4ca1abf6a",
    "104bc407-7054-48bd-91c3-c774043842e9",
    "0f1809dc-54ff-4230-bfec-fc751d1e64cc",
    "a88cb5be-36bc-44fb-b603-3bd7ad369e9d",
    "7ef31ed7-fe77-40aa-9236-6397d25a7730",
    "90dd8529-3ec0-4efe-afab-5d77a86cadcc",
    "6b173076-a0bd-46c4-a5b4-90661b10eecb",
    "191424a1-d110-4a22-88b8-51b2e4a54294",
    "facac6b9-9b0f-44ae-9f26-22502eaa5536",
    "6f83367e-c844-4a2b-b7be-03d5d88b7c17",
    "ad604b81-7336-4d8d-be54-6089f21b82b6",
    "a821ead2-1828-40f7-b480-82513b248424",
    "7ad9276b-5f03-4170-a2d5-526096506efd",
    "2b6bd8c6-27bb-4450-9a20-049e8b64a59f",
    "3b01f7ec-3449-4167-a809-0c4b946cdba1",
    "49a950c4-7d18-4f1f-9772-66c908a19627",
    "f110cbaa-d69b-495a-b41f-2a8a1cda6e4f",
    "bae87586-de82-4247-a2ce-9715f7cd9de2",
    "4c72035e-8f12-44f2-93e3-c535df3d575a",
    "f320c4ad-53ee-4bdd-86e6-786b3c99dc64",
    "777f5b20-5ad3-4a5b-99c6-59115bb83a47",
    "4e561522-297e-4424-a861-f6fe548cc43b",
    "d6e740aa-0352-40f8-8018-4bed16253af5",
    "a63e9d0b-e138-471a-a806-e7c88bf27a9e",
    "16bb20b6-9db5-4ff4-8d4b-03f1f80d5e87",
    "f5564f4d-72ed-4074-a494-1ad971b382aa",
    "d9b1d2be-2ba0-4ea7-a052-d40e25a3cfc6",
    "a47236f5-e1a8-4572-be1d-31a387094cc7",
    "0ed6ae7a-48ef-43e6-ac19-9c6433ca1c60",
    "5596cd4d-8b54-4484-a91e-bd2d9581b5dd",
    "97deb871-c3df-462a-9d4b-000f89b8975d",
    "ed49f615-3f50-4e94-ad93-d678055ac77a",
    "70853534-725b-4f1e-a654-b53e9fff105e",
    "51d922b3-1847-4ac1-b360-16dde22e456d",
    "e1a65c94-6484-4e5d-ab26-a736724f0863",
    "a1bd5d98-d44f-4ee4-a8db-9afc8907906a",
    "7acd1018-4bb7-4495-b6ea-f5eb5128b776",
    "7acc32e5-cd48-46f2-bd11-b39fe4f438d3",
    "646f1829-0145-4443-bb45-368032a4b2b0",
    "5edbe6e1-a393-4bfa-a36f-573af3742af4",
    "aba547af-ace6-4aef-a334-fdc3ff040fb4",
    "6a729e33-c959-4461-a324-c4fcf3d4e32b",
    "78921569-cd72-49b2-a128-4ba9560ed4dd",
    "7725c5d3-3ca3-424b-8f16-690d1edd669c",
    "8a4bad4c-c09b-45bc-aa6a-2b3a54dc8728",
    "8affa5c6-461f-41b2-a33e-06cde354be49",
    "b1f42171-2812-4494-9f54-7a45ffa29e43",
    "d610e6f6-bf29-4294-a0b7-e0daaa9ab7e6",
    "80d8ab32-197d-4300-bf3f-e172ddb74caa",
    "8539e09d-e52e-4826-8a71-d41bcfddb53b",
    "34538e30-d1a1-4924-a53d-5b22ab312f14",
    "492400e3-843f-41cb-bbd1-5a1a53242140",
    "808618b5-63b4-4fb0-95f9-d5f13731bf60",
    "d77703fa-be1e-49af-a152-620f6065879e",
    "1afa71e6-1f1f-433a-8f7b-daef49c91b11",
    "2ee37773-be6b-4a8f-b8d9-5976f6bdf6f3",
    "587aa494-a9f9-4830-a57f-baa62735a256",
    "c28eb3f8-6c29-470b-8128-b3c0c0c67d13",
    "953c95e2-8664-46dd-a989-3aa348286e90",
    "8cfe31c1-c1fa-44d3-b712-22935aac16a1",
    "d6c65f9e-d7d4-4c9f-8078-7b2c3da8c03a",
    "2ee125bb-aa59-4404-8d62-de1f96d6e438",
    "6bdc8e3e-79b0-4d5a-a47f-b91c6beb7bb8",
    "297a7380-4f16-42b5-bd68-df5cd15fa303",
    "645bceab-46e9-4955-80fe-836f08070bc5",
    "1c23f543-e609-4104-8f92-3b1566ec3872",
    "200f16d9-9d95-4048-b63f-28c915cbdb60",
    "5168a5a3-284f-4be6-90e1-22e88d0d74be",
    "996730bc-5aeb-446b-a8a5-a4851f564d14",
    "fc78d0ba-53bd-4ca9-8cee-9fca15ffc398",
    "6e21e364-569e-4be2-8058-542fdf2e28ac",
    "9dc7e078-5fd5-40a5-a9b2-c6682c21fc4d",
    "13c91c26-21ee-4384-9087-e13027869269",
    "026960b2-40f7-4ff9-925a-93fa015e355a",
    "9bd6b7a9-ed0e-45c1-9028-42b2fe59dfdf",
    "5fce234c-dee9-4914-9774-962f746608c8",
    "34d26acf-8de7-4f69-8c47-e50bfcccc399",
    "c664588c-7219-4295-bd99-98e4bff73929",
    "63373273-dde4-43ba-a0fa-049dd326029a",
    "5176a013-778d-4561-b0ed-b52af6e84f54",
    "b45fc786-000b-4aab-851d-6dd0105c0daf",
    "11b7a5d1-1626-4077-bd95-9bff611c29bd",
    "b6b07dc8-8582-494a-aa85-2bf054cf2732",
    "fcd95255-5e0a-40ad-a724-ec69bd6ae1ba",
    "a34dc1e8-e816-44d0-b9b1-d3609562af41",
    "d8d8758e-3acd-42ed-a2f7-103a992f90ec",
    "47b813aa-cece-4019-9add-adb5bb1f4e35",
    "0e71af96-dee8-4926-b23c-b7d3cac8474a",
    "b4d96586-9c66-425a-9c01-9c4446909bc2",
    "afe14e25-bb21-4ef1-bd76-7e3d1b5d858a",
    "bf544789-1be9-4e60-838d-6dddcdf2dd60",
    "c4fc7d5a-d3c6-42fe-81af-1fc2a092faf4",
    "dc8a661a-b5d4-425b-ba08-82a8b75f5d77",
    "df29e2d2-0a56-44ff-98fd-e18b0e0f7de1",
    "11888c48-7016-461b-9b84-3d82dffb01f2",
    "39cad6d5-26ea-4b60-a03e-628d1e058c85",
    "19f102dc-2d44-4422-be6c-b9283de75738",
    "ddc40162-a713-48c8-ad61-3a961d5308a4",
    "a03c8dbd-9078-46f1-9bef-e05ec8f9b2e9",
    "7575060f-3c36-4595-9127-9a59d3876e80",
    "9ba4bb6a-1b44-47f2-bac4-260db1c35ec8",
    "759dc505-42f7-4b96-9148-257b280259db",
    "fd77817c-5e04-40c9-b6b1-3d5587e354bc",
    "7e60346e-13fd-4eb8-947b-b2e072288280",
    "6a213881-1b4f-46a0-a2a8-cfbf3219ba14",
    "5fbda0da-87b5-4c78-994d-a7744f5bee5b",
    "9e80404c-f229-4b50-bccb-6c63c64c31b9",
    "0f856183-cc45-440c-90c2-2149688877bd",
    "c72cd35b-ba2a-40ed-bd00-502d35b2b82c",
    "31e2e359-d0c7-46e4-9cb4-8f1200fa9880",
    "4489fc75-4b06-41fa-b1a3-ec67edfe5252",
    "37f27e81-7a8c-4b30-b48a-b128a58ca5fa",
    "91402ec8-4fb2-4697-a6e9-47cc95f98bbf",
    "f0554749-b7c3-4982-a776-d0511b9ffd28",
    "4edb564d-a6f5-48d3-a860-05f515d8bd89",
    "bafee383-5b30-4746-a4e2-fb36d4eff599",
    "c32ab2fb-59c1-40a0-802c-1544bf1be4dc",
    "01295094-a506-4157-a4fd-d155e0284586",
    "d5e7c03f-a01b-4352-b86e-e79aeb616594",
    "26495555-b3d2-4de8-99f5-2a834d6fd1a3",
    "05f6891d-2a7c-46e3-a1b2-7aaa3180662d",
    "ce5482a7-f287-44a4-ae5b-0eff2e7037a7",
    "1a32dcf6-04dd-4b13-9a33-6340ebdd92b1",
    "d9d87cbe-a6e9-443c-aae1-d37525ed16f6",
    "6f389a32-ce3f-4716-b25d-ff4f8d57b613",
    "e06d5cc1-871a-48aa-8841-a4c7f0a3667a",
    "73fd68f9-7aa3-4344-a2cd-370fb9b05491",
    "9edede1f-9ef6-4fe1-b89e-d1d4d7230c42",
    "29389631-f4eb-4ef2-8858-bfeb60fbc18a",
    "ef8d7ffd-d56c-4c8a-80e2-2bc2654e7d19",
    "d828a45f-6ee9-432e-af4d-aef7c1293e75",
    "b694585c-c73f-4fc6-9285-c70d4478d544",
    "7c77d121-2795-4e96-a940-64211bf238e0",
    "b2ee2daa-198d-4ba0-a50d-c8e3b4c15f24",
    "1de78d1b-1ed8-45eb-a874-b0615875e475",
    "65755dbc-aeb1-4cf0-9fa0-39fbf268839f",
    "20a5fbf6-d835-4bf8-968d-449e16c4757f",
    "e28a6381-517d-40d6-ae45-667adb3656bc",
    "fdf9e530-cbd4-4c4c-b29f-2482fd68b249",
    "e36866ff-9f97-44cf-80d8-0cf3c96cc1f1",
    "a89de4e4-43ec-4bc7-b8de-eb97e02de54e",
    "41a56a80-ce7a-442d-92f5-0229e7457480",
    "e8b62ef0-e4e0-4508-8cf9-5a1f7a23ba9c",
    "63adc205-a92d-4251-ad8b-b5170d22e808",
    "0c10ed0a-905b-42d0-90f6-30ad4417ccd2",
    "8588f2c1-33fc-4708-8fed-4bd395de5b05",
    "97a726b5-aacb-4ff5-b655-f5d57abe8b05",
    "d8bdf923-b3c5-4d4e-a0b6-77d0f448f3e8",
    "bee3fdd2-e25b-4e99-b3a8-f166ed416ff3",
    "5cee3338-4f5a-4f02-b344-78d9692785a1",
    "62035fe1-f406-444d-b52b-4fd0a09f8b0c"];


if __name__ == '__main__':
    server = CoAPServerPlugTest('127.0.0.1', 40000)

    def create_resource(devid, rnum, rt):
        mr = MyResource()
        mr.path = "ResURI%d" % rnum
        mr.info = {'id': '%s' % devid,  'rt': 'oic.r.%s' % rt, 'value': False}

        print(json.dumps(mr.info))
        return mr

    def create_device(ip, port, rnum, dt, rt):
        global g_num
        global uuid_cache
        pat = '''{
            "di" : "%(uuid)s",
            "links" : [
                {
                    "href" : "coap://%(ip)s:%(port)d/oic/d",
                    "rel" : "contained",
                    "rt" : "oic.d.%(dt)s"
                },
                {
                    "href" : "coap://%(ip)s:%(port)d/ResURI%(rnum)d",
                    "rel" : "contained",
                    "rt" : "oic.r.%(rt)s"
                }
            ],
            "lt" : 86400,
            "n" : "%(name)s"
        }'''
        dinfo = {}
        
        dinfo['uuid'] = uuid_cache[g_num] # uuid.uuid4()
        dinfo['ip'] = ip
        dinfo['port'] = port
        dinfo['dt'] = dt
        dinfo['rt'] = rt
        dinfo['rnum'] = rnum
        dinfo['name'] = "name"+str(g_num) # uuid.uuid4()
        g_num += 1
        print(pat % dinfo)
        d = json.loads(pat % dinfo)
        m = create_resource(dinfo['uuid'], rnum, rt)
        return d, m

    def create_bell_device(ip, port, rnum, dt, rt):
        pat = '''{
            "di" : "%(uuid)s",
            "links" : [
                {
                    "href" : "coap://%(ip)s:%(port)d/oic/d",
                    "rel" : "contained",
                    "rt" : "oic.d.%(dt)s"
                },
                {
                    "href" : "coap://%(ip)s:%(port)d/ResURI%(rnum)d",
                    "rel" : "contained",
                    "rt" : "oic.r.%(rt)s"
                }
            ],
            "lt" : 86400,
            "n" : "%(name)s"
        }'''
        dinfo = {}
        dinfo['uuid'] = uuid.uuid4()
        dinfo['ip'] = ip
        dinfo['port'] = port
        dinfo['dt'] = dt
        dinfo['rt'] = rt
        dinfo['rnum'] = rnum
        dinfo['name'] = uuid.uuid4()

        print(pat % dinfo)
        d = json.loads(pat % dinfo)
        media = {'rel': 'contained', 'rt': 'oic.r.media', 'href': "coap://%s:%d/ResURI%d" % (ip, port, rnum)}
        d['links'].append(media)
        m = create_resource(dinfo['uuid'], rnum, rt)
        media = {'url': 'rtsp://admin:12345@192.168.1.188:554/Streaming/Channels/'
                    '1?transportmode=unicast&profile=Profile_1'}
        m.info['media'] = [media]
        return d, m

    def create_devices(ip, port):
        dl = []
        ml = []
        i = 1
        d, m = create_device(ip, port, i, "irintrusiondetector", 'sensor.motion')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "magnetismdetector", 'sensor.contact')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "magnetismdetector", 'sensor.contact')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "magnetismdetector", 'sensor.contact')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "magnetismdetector", 'sensor.contact')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "flammablegasdetector", 'sensor.carbonmonoxide')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "smokesensor", 'sensor.smoke')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "waterleakagedetector", 'sensor.water')
        dl.append(d)
        ml.append(m)
        i += 1

        d, m = create_device(ip, port, i, "Bellbuttonswitch", 'button')
        dl.append(d)
        ml.append(m)
        i += 1

        return dl, ml

    def post_devices(devs):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        '''s.setsockopt(socket.SOL_SOCKET, 25, 'eth0')'''
        s.bind(('0.0.0.0', 0))
        if platform.system() == "Windows":
            logger.info('rum DEMO Mode on ' + platform.system())
            client = HelperClient(server=('127.0.0.1', 5683), sock=s)
        else:
            client = HelperClient(server=('224.0.1.187', 5683), sock=s)
        

        try:
            for d in devs:
                request = client.mk_request(defines.Codes.POST, 'oic/rd')
                request.type = defines.Types['NON']
                request.payload = json.dumps(d)

                client.send_request(request, callback=None, timeout=1)
        except KeyboardInterrupt:
            client.close()
            return
        except Queue.Empty:
            pass

        timer = threading.Timer(30, post_devices, (devs,))
        timer.setDaemon(True)
        timer.start()


    class StaticHandler(tornado.web.RequestHandler):

        def get(self):
            self.write('It works')

    class OicHandler(tornado.web.RequestHandler):

        def get(self):
            global server

            self.write(json.dumps(server.reslist))

    class ChangeOicHandler(tornado.web.RequestHandler):

        def get(self):
            global server

            devid = self.get_argument('id')
            print(server.reslist[devid])
            oldval = server.reslist[devid]['value']

            server.reslist[devid]['value'] = not oldval
            o = server.obs[devid]
            o.payload = json.dumps(o.info)
            server.notify(o)
            print(oldval)

            self.write('{}')


    class WebSocketHandler(tornado.websocket.WebSocketHandler):
        """docstring for SocketHandler"""
        clients = set()

        def check_origin(self, origin):
            return True

        @staticmethod
        def send_to_all(message):
            print(json.dumps(message))
            for c in WebSocketHandler.clients:
                c.write_message(json.dumps(message))

        def open(self):
            WebSocketHandler.clients.add(self)

        def on_close(self):
            WebSocketHandler.clients.remove(self)

        def on_message(self, message):
            pass



    dlist, rlist = create_devices('127.0.0.1', 40000)
    server.add_resources(rlist)
    post_devices(dlist)
    t = threading.Thread(target=server.listen, args=(10,))
    t.setDaemon(True)
    t.start()
    wapp = tornado.web.Application(
        handlers=[
            (r"/ws", WebSocketHandler),
            (r"/", StaticHandler),
            (r"/get_oicinfo", OicHandler),
            (r"/change_oicinfo", ChangeOicHandler)
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
    )
    try:
        wapp.listen(8000)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "Server Shutdown"
        tornado.ioloop.IOLoop.instance().stop()
        server.close()
        t.join(1)
        print "Exiting..."
