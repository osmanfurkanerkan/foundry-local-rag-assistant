# Generate embeddings with Azure OpenAI

Kaynak: https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/embeddings

An embedding is a vector of floating-point numbers that represents the semantic meaning of text. Similar text produces vectors that are close together, which makes embeddings useful for vector search, recommendations, classification, and clustering.

## Prerequisites

* An Azure subscription. [Create one for free](https://azure.microsoft.com/free/) if you don't have one.
* An Azure OpenAI resource with an embedding model deployment.
* Your resource endpoint, such as `https://YOUR-RESOURCE-NAME.openai.azure.com`.
* For Microsoft Entra ID authentication, an identity with the `Cognitive Services OpenAI User` role assigned to the Azure OpenAI resource. For more information, see [Role-based access control for Azure OpenAI](/en-us/azure/ai-foundry/openai/how-to/role-based-access-control).
* The [Azure CLI](/en-us/cli/azure/install-azure-cli) for local authentication.
* The runtime and package manager for the language you select.

For more language-specific setup guidance, see [Azure OpenAI supported programming languages](../supported-languages).

The `model` value in each request is your Azure model deployment name. The examples use `text-embedding-3-small`; replace it if your deployment has a different name.

## Generate an embedding

Send text to the embeddings endpoint, and read the vector from the first item in the response.

The v1 embeddings API supports Microsoft Entra ID and API key authentication. Microsoft Entra ID is recommended because it avoids storing long-lived credentials. The examples in this article use Microsoft Entra ID.

For local development, sign in to Azure before you run an SDK example:

```
az login
```

`DefaultAzureCredential` uses your signed-in identity locally and can use a managed identity when your application runs in Azure.

API key authentication is also supported. For key-based client configuration, see [Azure OpenAI v1 API guidance](../api-version-lifecycle).

* [Python](#tabpanel_1_python-new)
* [C#](#tabpanel_1_csharp)
* [JavaScript](#tabpanel_1_javascript)
* [Java](#tabpanel_1_java)
* [Go](#tabpanel_1_go)
* [PowerShell](#tabpanel_1_PowerShell)
* [REST](#tabpanel_1_console)

Install the OpenAI and Azure Identity packages:

```
pip install openai azure-identity
```

Generate an embedding and print its dimensions:

```
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

endpoint = "https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/"
token_provider = get_bearer_token_provider(
	DefaultAzureCredential(), "https://ai.azure.com/.default"
)
openai = OpenAI(
	base_url=endpoint,
	api_key=token_provider,
)

# Generate one embedding vector.
response = openai.embeddings.create(
	model="text-embedding-3-small",
	input="The quick brown fox jumped over the lazy dog.",
)
print(f"Embedding dimensions: {len(response.data[0].embedding)}")
```

```
Embedding dimensions: <number>
```

Reference: [`embeddings.create`](https://github.com/openai/openai-python/blob/main/src/openai/resources/embeddings.py)

## Best practices

Tip

Embedding requests return HTTP 400 when the **sum** of input tokens exceeds 300,000, even if every individual input is under the per-input limit. Split large batches into smaller requests.

### Verify inputs don't exceed the maximum length

* The maximum input length for the current embedding models is 8,192 tokens. Check each input before sending the request.
* If you send an array of inputs in a single embedding request, the maximum array size is 2,048.
* Each `/embeddings` request has a 300,000-token aggregate limit across all inputs. Requests above this limit fail with HTTP 400.
* Keep the total tokens per minute below the quota assigned to your model deployment. For current limits, see [Azure OpenAI quotas and limits](../quotas-limits).

## Troubleshooting

* For a `401` response, sign in again and confirm that the access token uses the correct audience.
* For a `403` response, confirm that your identity has the `Cognitive Services OpenAI User` role assigned to the Azure OpenAI resource.
* For a `404` response, confirm that the endpoint includes `/openai/v1/` and that `model` contains a valid deployment name.
* For a `400` response, check the request body, each input's token count, the number of inputs, and the aggregate token count.

## Limitations and risks

Embedding models might be unreliable or pose social risks in certain cases. They might cause harm if used without mitigations. For more information about how to approach their use responsibly, see the [Responsible AI](/en-us/azure/foundry/responsible-use-of-ai-overview) content.

## Next steps

* [Explore embeddings and document search](../tutorials/embeddings).
* [Review available Azure OpenAI models](../../foundry-models/concepts/models-sold-directly-by-azure).
* Choose a service to store and search vectors:
  + [Azure AI Search](/en-us/azure/search/vector-search-overview)
  + [Azure SQL Database](/en-us/azure/azure-sql/database/ai-artificial-intelligence-intelligent-applications?view=azuresql&preserve-view=true#vector-search)
  + [Azure Cosmos DB for NoSQL](/en-us/azure/cosmos-db/nosql/vector-search)
  + [Azure Database for PostgreSQL flexible server](/en-us/azure/postgresql/flexible-server/how-to-use-pgvector)
  + [Azure Managed Redis](/en-us/azure/redis/overview-vector-similarity)
  + [Eventhouse in Microsoft Fabric](/en-us/fabric/real-time-intelligence/vector-database)
