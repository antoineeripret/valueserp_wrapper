# ValueSERP Wrapper for Python (by Antoine Eripret)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Package purpose and content
`valueserp_wrapper` is a wrapper around the [ValueSERP](https://www.valueserp.com/) API. It allows you to use the API effortlessly in your Python projects. There are other SERP API available, but ValueSERP is one of the most complete and cost-effective out there. Also, it's the one I use the most. 

*DISCLAIMER*: this library is not affiliated with ValueSERP in any way. It's a simple wrapper that I made to facilitate my use of the API.

## Installation Instructions
First, install the package using:

`pip3 install git+https://github.com/antoineeripret/valueserp_wrapper`

## Quickstart

- Create an account on [ValueSERP](https://www.valueserp.com/)
- Choose your plan amongst the two options available [here](https://www.valueserp.com/pricing). For ad-hoc analysis, I strongly advise to go with the "Pay as you go" option. It's the most flexible and the one I use. 
- Get your API key and copy it somewhere to use it later on in your code. 

## Usage 

First of all, import the package:

```python
import valueserpwrapper
```

### Account 

You can create an `Account` object with your API key:

```python
account = valueserpwrapper.Account(api_key)
```

This `Account` object can be used to perform the following actions:

- Get information about your account, such as your plan and the number of credits available. More information about the information returned [here](https://www.valueserp.com/docs/account-api).

```python
account.info()
```

- Find locations based on a search query. To run a search through the API, you need to provide a location. However, you can use this method to check what are the possible locations that you can use in your searches. For instance: 

```python
account.find_locations("Paris")
```

This will return a dataframe with the possible locations based on your search query (in our case, "Paris") and you can then choose the one you want to use in your searches.  

- Run a search. Sometimes, you need to run a single search to check what information is being returned. You can do so with the `make_search` method. For instance: 

```python
search = account.make_search("pizza", "Paris,Paris,Ile-de-France,France")
```

This will return a `Search` object with the results of the search. This object is documented below.  

### Batch

One of the most powerful features of ValueSERP is the ability to run multiple searches in a single request. You can do so with the `Batch` object. 

1. Create a batch with your `Account` object:

```python
batch = account.create_batch('My batch')
```

By defaukt, the batch accepts every `search_type` available [here]I(https://www.valueserp.com/docs/batches-api/batches/create), but if you want to restrict it, you can use the `search_type` parameter. For example: 

```python
batch = account.create_batch(name="My batch", search_type="places")
```

2. Create the `Batch` object 

When you run the `create_batch` method, it prints the batch id. You need to keep it to create the `Batch` object. For example: 

```python
batch = valueserpwrapper.Batch(api_key, "123456")
```

3. Add searches to the batch:

You can then add searches to the batch. You can add up to 15,000 searches per batch. *There is a built-in check to ensure that you don't add more than that*. However, you can add more than one batch to your account, but this operation is not handled automatically by the wrapper. 

```python
#list of dictionnaries. Each dictionnary represent a search. 

searches = [
  {
  "q": "mcdonalds",
  "location": "United States",
  "search_type": "images",
}]

#add the searches to the batch
batch.add_searches(searches)
```

The list of parameters for each search is available [here](https://www.valueserp.com/docs/search-api/searches/common). 


4. Launch the batch:

```python
batch.start()
```

This will start the batch and return a message saying that the batch was started. Under the hood, ValueSERP will process the batch and store the result in their servers. This process takes some time, and you can check the status of the batch with the `info` method. 

```python
batch.info()
```

This will return a dictionnary and the `status` key will give you information about the status of the batch. 

5. Get the result of the batch:

In ValueSERP, the result of a batch is called a *result set*. You can get the result set with the `get_result_set` method. 

```python
batch.get_result_set()
```

This will return a `Searches` object with the results of the batch. This object is documented below. By default, it returns the last available result set. However, you can specify which result set you want to get by passing the `result_set_id` parameter. For example: 

```python
batch.get_result_set(result_set_id="123456")
```

This `result_set_id` is the id of the result set that you can get with the `list_result_sets` method. 

```python
batch.list_result_sets()
```

### Search

The `Search` object is only used when you call the `make_search` method from the `Account` object. It's a simple object that contains the data returned by ValueSERP. 

```python
search = account.make_search("pizza", "Paris,Paris,Ile-de-France,France")
```

This object has two methods that are worth noting: 

- `available_attributes`: This method returns the list of attributes available in the `Search` object. 

```python
search.available_attributes()
```

- `to_dataframe`: This method converts the data returned by ValueSERP into a pandas dataframe. You need to specify the attribute you want to convert. For example: 

```python
search.to_dataframe("organic_results")
```

This will return a dataframe with the organic results of the search. 

### Searches 

The `Searches` object is only used when you call the `get_result_set` method from the `Batch` object. It's a list of `Search` objects. 

```python 
result = batch.get_result_set()
```


This object has two several that are worth noting: 

- `available_attributes`: This method returns the list of attributes available in the `Searches` object and that are compatible with the `to_dataframe` method. 


```python
result.available_attributes()
```

- `to_dataframe`: This method converts the data returned by ValueSERP into a pandas dataframe. You need to specify the attribute you want to convert. For example: 

```python
result.to_dataframe("organic_results")
```

This will return a dataframe with the organic results of the search. 

- `raw_json`: This method returns the raw json returned by ValueSERP. It is useful if the attribute you are looking for is not available in the `available_attributes` method. 

```python
result.raw_json()
```

- `get_rankings`: This method returns the rankings of a domain in the organic results. It is useful to check the organic position of a domain in the SERP. For example: 

```python
result.get_rankings("www.mcdonalds.com")
```

This will return a dataframe with the rankings of www.mcdonals.es in the organic results. Be sure to use the domain as it is, with or without the www. based on your structure. 