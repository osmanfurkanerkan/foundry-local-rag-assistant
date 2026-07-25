# Generate embeddings for search queries and documents

Kaynak: https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-generate-embeddings

Note

Azure AI Search is available through the [Azure portal](https://portal.azure.com), [REST APIs](/en-us/azure/search/search-api-versions#rest-apis), and [Azure SDKs](/en-us/azure/search/search-api-versions#all-azure-sdks). It also underpins [Foundry IQ](/en-us/azure/foundry/agents/concepts/what-is-foundry-iq), the managed knowledge layer that transforms enterprise content into reusable, permission-aware knowledge bases for agents in the [Microsoft Foundry portal](https://ai.azure.com/?cid=learnDocs).

Azure AI Search doesn't host embedding models, so you're responsible for creating vectors for query inputs and outputs. Choose one of the following approaches:

| Approach | Description |
| --- | --- |
| [Integrated vectorization](vector-search-integrated-vectorization) | Use built-in data chunking and vectorization in Azure AI Search. This approach takes a dependency on indexers, skillsets, and built-in or custom skills that point to external embedding models, such as those in Microsoft Foundry. |
| Manual vectorization | Manage data chunking and vectorization yourself. For indexing, you [push prevectorized documents](vector-search-how-to-create-index#load-vector-data-for-indexing) into vector fields in a search index. For querying, you [provide precomputed vectors](#generate-an-embedding-for-an-ad-hoc-query) to the search engine. For demos of this approach, see the [azure-search-vector-samples](https://github.com/Azure/azure-search-vector-samples/tree/main) GitHub repository. |

We recommend integrated vectorization for most scenarios. Although you can use any supported embedding model, this article uses Azure OpenAI models for illustration.

## How embedding models are used in vector queries

Embedding models generate vectors for both query inputs and query outputs. Query inputs include:

* **Text or images that are converted to vectors during query processing**. As part of integrated vectorization, a [vectorizer](vector-search-how-to-configure-vectorizer) performs this task.
* **Precomputed vectors**. You can generate these vectors by passing the query input to an embedding model of your choice. To avoid [rate limiting](/en-us/azure/ai-services/openai/quotas-limits), implement retry logic in your workload. Our [Python demo](https://github.com/Azure/azure-search-vector-samples/tree/93c839591bf92c2f10001d287871497b0f204a7c/demo-python) uses [tenacity](https://pypi.org/project/tenacity/).

Based on the query input, the search engine retrieves matching documents from your search index. These documents are the query outputs.

Your search index must already contain documents with one or more vector fields populated by embeddings. You can create these embeddings through integrated or manual vectorization. To ensure accurate results, use the same embedding model for indexing and querying.

## Tips for embedding model integration

* **Identify use cases**. Evaluate specific use cases where embedding model integration for vector search features adds value to your search solution. Examples include [multimodal search](multimodal-search-overview) or matching image content with text content, multilingual search, and similarity search.
* **Design a chunking strategy**. Embedding models have limits on the number of tokens they accept, so [data chunking](vector-search-how-to-chunk-documents) is necessary for large files.
* **Optimize cost and performance**. Vector search is resource intensive and subject to maximum limits, so vectorize only the fields that contain semantic meaning. [Reduce vector size](vector-search-how-to-configure-compression-storage) to store more vectors for the same price.
* **Choose the right embedding model**. Select a model for your use case, such as word embeddings for text-based searches or image embeddings for visual searches. Consider pretrained models, such as text-embedding-ada-002 from OpenAI or the Image Retrieval REST API from [Azure Vision in Foundry Tools](/en-us/azure/ai-services/computer-vision/how-to/image-retrieval).
* **Normalize vector lengths**. To improve the accuracy and performance of similarity search, normalize vector lengths before you store them in a search index. Most pretrained models are already normalized.
* **Fine-tune the model**. If needed, fine-tune the model on your domain-specific data to improve its performance and relevance to your search application.
* **Test and iterate**. Continuously test and refine the embedding model integration to achieve your desired search performance and user satisfaction.

## Create resources in the same region

Although integrated vectorization with Azure OpenAI embedding models doesn't require resources to be in the same region, using the same region can improve performance and reduce latency.

To use the same region for your resources:

1. Check the [regional availability of text embedding models](/en-us/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability).
2. Check the [regional availability of Azure AI Search](search-region-support).
3. Create an Azure OpenAI resource and Azure AI Search service in the same region.

Tip

Want to use [semantic ranking](semantic-how-to-query-request) for [hybrid queries](hybrid-search-overview) or a machine learning model in a [custom skill](cognitive-search-custom-skill-interface) for [AI enrichment](cognitive-search-concept-intro)? Choose an Azure AI Search region that provides those features.

## Choose an embedding model in Foundry

When you add knowledge to an agent workflow in the [Foundry portal](https://ai.azure.com/?cid=learnDocs), you have the option of creating a search index. A wizard guides you through the steps.

One step involves selecting an embedding model to vectorize your plain text content. The following models are supported:

* text-embedding-3-small
* text-embedding-3-large
* text-embedding-ada-002
* Cohere-embed-v3-english
* Cohere-embed-v3-multilingual

Your model must already be deployed, and you must have permission to access it. For more information, see [Deployment overview for Foundry Models](/en-us/azure/ai-foundry/concepts/deployments-overview).

## Generate an embedding for an ad hoc query

If you don't want to use integrated vectorization, you can manually generate an embedding and paste it into the `vectorQueries.vector` property of a vector query. For more information, see [Create a vector query in Azure AI Search](vector-search-how-to-query).

The following examples assume the text-embedding-ada-002 model. Replace `YOUR-API-KEY` and `YOUR-OPENAI-RESOURCE` with your Azure OpenAI resource details.

* [.NET](#tabpanel_1_dotnet)
* [Java](#tabpanel_1_java)
* [JavaScript](#tabpanel_1_javascript)
* [Python](#tabpanel_1_python)
* [REST API](#tabpanel_1_rest-api)

```
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

class Program
{
    static async Task Main(string[] args)
    {
        var apiKey = "YOUR-API-KEY";
        var apiBase = "https://YOUR-OPENAI-RESOURCE.openai.azure.com";
        var apiVersion = "2024-02-01";
        var engine = "text-embedding-ada-002";

        var client = new HttpClient();
        client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

        var requestBody = new
        {
            input = "How do I use C# in VS Code?"
        };

        var response = await client.PostAsync(
            $"{apiBase}/openai/deployments/{engine}/embeddings?api-version={apiVersion}",
            new StringContent(JsonConvert.SerializeObject(requestBody), Encoding.UTF8, "application/json")
        );

        var responseBody = await response.Content.ReadAsStringAsync();
        Console.WriteLine(responseBody);
    }
}
```

The output is a vector array of 1,536 dimensions.

## Related content

* [Understand embeddings in Azure OpenAI in Foundry Models](/en-us/azure/ai-services/openai/concepts/understand-embeddings)
* [Generate embeddings with Azure OpenAI](/en-us/azure/ai-services/openai/how-to/embeddings?tabs=console)
* [Tutorial: Explore Azure OpenAI embeddings and document search](/en-us/azure/ai-services/openai/tutorials/embeddings?tabs=command-line)
