#library to make http requests 
import requests 
#library to handle data 
import pandas as pd 

#list of search types that we can use for the ValueSERP API
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

#class to handle the account information 
class Account: 
    def __init__(self, api_key):
        #api needed to use the ValueSERP API
        self.api_key = api_key
        #endpoints to make requests to the ValueSERP API
        self.endpoints = {
            #retrieve all the locations available  for the API 
            'locations': 'https://api.valueserp.com/locations',
            #retrieve information about the account 
            #this endpoint is needed to ensure that we have enough credits to run our searches
            'info': 'https://api.valueserp.com/account', 
            #endpoint to make a search 
            'search':'https://api.valueserp.com/search', 
            #endpoint to create a batch 
            'create_batch':f'https://api.valueserp.com/batches?api_key={api_key}', 
            #endpoint to delete a batch 
            'delete_batch':f'https://api.valueserp.com/batches/batch_id?api_key={api_key}', 
            #endpoint to list all the batches in our account 
            'list_batches': 'https://api.valueserp.com/batches'
        }
    
    def __repr__(self):
        info = self.info()
        
        return """
    <valueserp.account(
        api_key='{}',
        email='{}',
        plan='{}', 
    )>""".format(
            info['api_key'],
            info['email'],
            info['plan']
        )
        
    #method to get information about the account 
    def info(self):
        params = {
            'api_key': self.api_key
        }
        # make the http GET request to VALUE SERP
        api_result = requests.get(self.endpoints.get('info'), params)
        # get the JSON response from VALUE SERP
        return api_result.json()['account_info']
        
    #method to find the available locations based on a search query 
    def find_locations(self, place): 
        params = {
            'api_key': self.api_key, 
            'q': place
        }
        # make the http GET request to VALUE SERP
        api_result = requests.get(self.endpoints.get('locations'), params)
        # get the JSON response from VALUE SERP
        return pd.json_normalize(api_result.json()['locations'])
    
    #method to make a search 
    #only advisef for individual searches to understand what is being returned by the API 
    def make_search(self, query, location, num=100): 
        params = {
            'api_key': self.api_key,
            'q': query,
            'location': location, 
            'num': num
        }
        #check that the location is valid 
        locations = self.find_locations(location)
        if len(locations) == 0:
            raise ValueError('The location is not valid. Please check the available locations using the find_locations method.')
        elif location not in locations['full_name'].values:
            raise ValueError('The location is not valid. Please check the available locations using the find_locations method.')
        # make the http GET request to VALUE SERP
        api_result = requests.get(self.endpoints.get('search'), params)
        #get the JSON response from VALUE SERP
        return Search(api_result.json())
    
    #method to create a batch 
    #a batch is a collection of searches that we want to run in a single request 
    #a batch can have a maximum of 15,000 searches 
    def create_batch(self, name, search_type='mixed'):
        #check if the search type is valid 
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
            
    #method to delete a batch 
    def delete_batch(self, batch_id):
        params = {
            'api_key': self.api_key
        }
        #make the request 
        api_result = requests.delete(self.endpoints.get('delete_batch').replace('batch_id', batch_id), params)
        #get the response 
        api_response = api_result.json()
        if api_response['request_info']['success'] == False:
            print('The batch was not deleted!!!')
            print('The API returned an unsuccessful response.')
        else:
            print('The batch was deleted successfully!')
            print(f'The batch id was {batch_id}')
    
    #list all the batches in our account 
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
    
    #method to get the available attributes in our object 
    def available_attributes(self):
        return [key for key in self.__dict__.keys()]
    
    #in some cases, we may want to convert the data into a a dataframe
    def to_dataframe(self, attr): 
        #check that the attribute exists 
        if attr not in self.available_attributes():
            raise ValueError(f'The attribute {attr} does not exist. Please check the available attributes using the available_attributes method.')
        #return the dataframe with the requested data 
        return pd.json_normalize(getattr(self, attr))

#class to handle the batch  
class Batch: 
    def __init__(self, api_key, batch_id):
        self.api_key = api_key
        self.account = Account(self.api_key)
        #double check that the batch id is correct 
        if batch_id not in self.account.list_batches()['id'].values:
            raise ValueError('The batch id does not exist in your account.')
        self.batch_id = batch_id
        self.endpoints = {
            #endpoint to start a batch 
            'start_batch':f'https://api.valueserp.com/batches/{self.batch_id}/start', 
            #endpoint to delete a batch 
            'delete_batch':f'https://api.valueserp.com/batches/{self.batch_id}?api_key={self.api_key}', 
            #endpoint to get information about the batch 
            'info':f'https://api.valueserp.com/batches/{self.batch_id}', 
            #endpoint to list the searches in a batch 
            'list_searches': f'https://api.valueserp.com/batches/{self.batch_id}/searches/page_number', 
            #endpoint to clear all the searches in a batch 
            'clear_all_searches': f'https://api.valueserp.com/batches/{self.api_key}/clear?api_key={self.api_key}', 
            #endpoint to add searches to a batch 
            'add_searches': f'https://api.valueserp.com/batches/{self.batch_id}?api_key={self.api_key}', 
            #endpoint to list the result sets in a batch 
            'list_result_sets':f'https://api.valueserp.com/batches/{self.batch_id}/results', 
            #endpoint to get a specific result set in a batch 
            'get_result_set':f'https://api.valueserp.com/batches/{self.batch_id}/results/result_set_id'
        }
        
    #method to get information about the batch 
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
            if api_response['request_info']['success'] == False:
                print(api_response  )
                raise ValueError('The API returned an unsuccessful response.')
        
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
        #raw response 
        self.searches = searches
        #create a list of unique keys for our searches
        self.keys = set(key for dict_item in searches for key in dict_item.keys())
        #create attributes based on those keys 
        for key in self.keys:
            setattr(self, key, [dict_item.get(key) for dict_item in searches])
    
    #method to get the available attributes in our object 
    def available_attributes(self):
        return [
            key 
            for key 
            in self.__dict__.keys() 
            #remove keys thta are not compatible with our to_dataframe method 
            if key not in ['keys', 'search_parameters', 'search_metadata', 'search_information','pagination','local_results_more_link','knowledge_graph']
        ]
    
    def raw_json(self):
        return self.searches 
    
    def to_dataframe(self, attr): 
        #check that the attribute exists 
        if attr not in self.available_attributes():
            raise ValueError(f'The attribute {attr} does not exist. Please check the available attributes using the available_attributes method.')
        if attr in ['keys', 'search_parameters', 'search_metadata', 'search_information','pagination','local_results_more_link','knowledge_graph']: 
            raise ValueError('This method is not compatible with the requested attribute. Use the raw_json method to access this data.')

        #the dataframe where we'll store our data 
        df = pd.DataFrame()
        #loop the results and store them in a dataframe 
        for count, element in enumerate(getattr(self, attr)):
            df = (
                pd
                .concat(
                    [df, 
                    pd.DataFrame(element)
                    .assign(
                        query = getattr(self, 'search_parameters')[count].get('q'),
                        location = getattr(self, 'search_parameters')[count].get('location'),
                        engine = getattr(self, 'search_parameters')[count].get('engine'),
                        id = getattr(self, 'search_parameters')[count].get('id')
                        ), 
                    ], 
                    ignore_index=True
                )
            )
        
        return df 
    
    #method to get the rankings of a domain in the organic results 
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
        