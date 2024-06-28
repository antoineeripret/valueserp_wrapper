#requires libraries
import requests 
import json 
import pandas as pd 

#available search types in the API 
SEARCH_TYPE = [
    'mixed', 
    'web',
    'news',
    'images',
    'videos',
    'places',
    'place_details',
    'shopping', 
    'product',
    'product_sellers_online',
    'product_sellers_local',
    'product_reviews',
    'product_specifications',
]

#object for most common manipulations
class Account: 
    def __init__(self, api_key):
      #API key is required 
        self.api_key = api_key
      #most common endpoints for our manipulations 
        self.endpoints = {
            'locations': 'https://api.valueserp.com/locations', 
            'info': 'https://api.valueserp.com/account', 
            'search':'https://api.valueserp.com/search', 
            'create_batch':f'https://api.valueserp.com/batches?api_key={api_key}', 
            'list_batches': 'https://api.valueserp.com/batches'
        }
    
    def info(self):
        params = {
            'api_key': self.api_key
        }
        
        # make the http GET request to VALUE SERP
        api_result = requests.get(self.endpoints.get('info'), params)

        # get the JSON response from VALUE SERP
        return api_result.json()['account_info']
        
        
    def find_locations(self, place): 
        params = {
            'api_key': self.api_key, 
            'q': place
        }
        
        # make the http GET request to VALUE SERP
        api_result = requests.get(self.endpoints.get('locations'), params)

        # get the JSON response from VALUE SERP
        return pd.json_normalize(api_result.json()['locations'])
    
    def make_search(self, query, location, num=100): 
        params = {
            'api_key': self.api_key,
            'q': query,
            'location': location, 
            'num': num
        }
        
        # make the http GET request to VALUE SERP
        api_result = requests.get(self.endpoints.get('search'), params)
        
        #get the JSON response from VALUE SERP
        return Search(api_result.json())
    
    #create a batch
    def create_batch(self, name, search_type='mixed'):
        
        if search_type not in SEARCH_TYPE:
            raise ValueError(f"search_type must be one of {SEARCH_TYPE}")
        
        body = {
            "name": name,
            "enabled": True,
            "schedule_type": 'manual',
            "priority": "normal",
            "search_type": search_type,
        }
        
        #make the request 
        api_result = requests.post(self.endpoints.get('create_batch'), json=body)
        #get the response 
        api_response = api_result.json()
        #raise an error if the creation was unsuccessful
        if api_response['request_info']['success'] == False:
            print('Te batch was not created!!!')
            print('The APÎ returned an unsuccessful response.')
        else:
            print('The batch was created successfully!')
            print(f'The batch id is {api_response["batch"]["id"]}')
    
    #list all the batches
    def list_batches(self):
        params = {
            'api_key': self.api_key
        }
        api_result = requests.get('https://api.valueserp.com/batches',  params = params)
        api_response = api_result.json()
        return pd.DataFrame(api_response['batches'])


class Search:
    def __init__(self, json_response):
        #we set all the attributes based on the returned json 
        for key, value in json_response.items():
            setattr(self, key, value)
    
    #in some cases, we may want to convert the data into a a dataframe
    def to_dataframe(self, attr): 
        return pd.json_normalize(getattr(self, attr))

class Batch: 
    def __init__(self, api_key, batch_id):
        self.api_key = api_key
        self.account = Account(self.api_key)
        if batch_id not in self.account.list_batches()['id'].values:
            raise ValueError('The batch id does not exist in your account.')
        self.batch_id = batch_id
        self.endpoints = {
            'start_batch':f'https://api.valueserp.com/batches/{self.batch_id}/start', 
            'delete_batch':f'https://api.valueserp.com/batches/{self.batch_id}?api_key={self.api_key}', 
            'info':f'https://api.valueserp.com/batches/{self.batch_id}', 
            'list_searches': f'https://api.valueserp.com/batches/{self.batch_id}/searches/page_number', 
            'clear_all_searches': f'https://api.valueserp.com/batches/{self.api_key}/clear?api_key={self.api_key}', 
            'add_searches': f'https://api.valueserp.com/batches/{self.batch_id}?api_key={self.api_key}', 
            'list_result_sets':f'https://api.valueserp.com/batches/{self.batch_id}/results', 
            'get_result_set':f'https://api.valueserp.com/batches/{self.batch_id}/results/result_set_id'
        }
        
    def info(self):
        params = {
            'api_key': self.api_key
        }
        
        api_result = requests.get(self.endpoints.get('info'), params)
        api_response = api_result.json()
        return api_response
    
    #delete a batch 
    def delete_batch(self):
        #make the request
        api_result = requests.delete(self.endpoints.get('delete_batch'))
        
        #display the result
        api_response = api_result.json()
        if api_response['request_info']['success'] == False:
            print('The batch was not deleted!!!')
            print('The API returned an unsuccessful response.')
        else:
            print('The batch was deleted successfully!')
            print(f'The batch id was {self.batch_id}')
        
    #start a batch 
    def start(self):
        params = {
            'api_key': self.api_key
        }

        api_result = requests.get(self.endpoints.get('start_batch'), params)
        api_response = api_result.json()
        print(f"Batch started: {self.batch_id}")
    
    #list searches 
    def list_searches(self):
        #get first the number of pages we have in the batch 
        pages = self.info()['batch']['searches_page_count']
        if pages == 0:
            raise ValueError('The batch has no searches.')
        #create a list from 1 to the number of pages included 
        pages = list(range(1, pages+1))
        
        params = {
            'api_key': self.api_key
        }
        
        searches = []
        for page in pages: 
            api_result = requests.get(self.endpoints.get('list_searches').replace('page_number', str(page)), params)
            searches.extend(api_result.json()['searches'])
        
        return pd.DataFrame(searches)
    
    def clear_all_searches(self):
        api_result = requests.delete(self.endpoints.get('clear_all_searches'))
        if api_result.json()['request_info']['success'] == False:
            print('The batch was not cleared!!!')
            print('The API returned an unsuccessful response.')
        else:
            print('The batch was cleared successfully!')
            print(f'The batch id is {self.batch_id}')
    
    def get_number_of_searches(self):
        return self.info()['batch']['searches_total_count']
    
    def add_searches(self, searches:list):
        if len(searches) > 15000 - self.get_number_of_searches():
            raise ValueError('A batch cannot have more than 15,000 searches. Create more than one batch.')
        
        #divide our seraches in chunks of 1000
        chunks = [searches[x:x+1000] for x in range(0, len(searches), 1000)]
        #iterate over the chunks and add our searches to our batch 
        for chunk in chunks:
            body = {
                "searches": [
                    search for search in chunk
                ]
            }
            api_result = requests.put(self.endpoints.get('add_searches'), json=body)
            api_response = api_result.json()
        
        print(f'{len(searches)} searches were added to the batch {self.batch_id}.')
        
    def list_result_sets(self):
        params = {
        'api_key': self.api_key
        }
        api_result = requests.get(self.endpoints.get('list_result_sets'), params)
        api_response = api_result.json()
        return pd.json_normalize(api_response['results'])
    
    def get_result_set(self, result_set_id=None):
        #get the last available 
        if result_set_id == None:
            result_sets = self.list_result_sets()
            if len(result_sets) == 0:
                raise ValueError('The batch has no result sets.')
            else: 
                result_set_id = result_sets.id.values[0]
        elif result_set_id not in self.list_result_sets()['id'].values:
            raise ValueError('The result set id does not exist for this batch.')
        
        #get the result set
        params = {
        'api_key': self.api_key
        }

        api_result = requests.get(self.endpoints.get('get_result_set').replace('result_set_id',str(result_set_id)), params)
        api_response = api_result.json()
        download_urls = api_response['result']['download_links']['pages']
        return Searches(pd.concat([pd.read_json(page)['result'] for page in download_urls]).tolist())
    


class Searches:
    def __init__(self, searches):
        #create a list of unique keys for our searches
        self.keys = set(key for dict_item in searches for key in dict_item.keys())
        #create attributes based on those keys 
        for key in self.keys:
            setattr(self, key, [dict_item.get(key) for dict_item in searches])
        
    #in some cases, we may want to convert the data into a a dataframe
    def to_dataframe(self): 
        
        def remove_elements_by_index(list, indexes):
            for index in sorted(indexes, reverse=True): 
                del list[index]
            return list
        
        #if we have no data 
        none_indices = [index for index, element in enumerate(getattr(self, 'organic_results')) if element is None]

        return (
            pd
            .DataFrame([element[0] for element in remove_elements_by_index(getattr(self, 'organic_results'), none_indices)])
            .merge(
                pd.
                DataFrame(remove_elements_by_index(getattr(self, 'search_parameters'), none_indices))
                .filter(items=['q','device','location','google_domain']), 
                left_index=True,
                right_index=True, 
                how='left'
            )
        )
    
    def get_rankings(self, domain):
        data = self.to_dataframe()
        return (
            data
            .filter(items=['q'])
            .drop_duplicates(keep='first', ignore_index=True)
            .merge(
                data
                .query('domain == @domain')
                .drop_duplicates(subset=['q','domain'], keep='first')
                .filter(items=['q','position','link']), 
                how='left',
                on='q'                
            )
        )
        
