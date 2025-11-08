import sys
import os
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
from backend.vector_store import VectorStore
vs = VectorStore()
ids = vs.add_documents([{'content':'Jammu is a city in northern India, capital of the Indian-administered union territory of Jammu and Kashmir. It is known for temples, scenic valleys, and access to the Himalayas. Popular activities include visiting Vaishno Devi, trekking, and sampling local cuisine.','metadata':{'source':'test_jammu'}}])
print('added', ids)
