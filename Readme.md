# Knowledge Graph Explorer

Imagine a smart tool that helps researchers connect the dots between genes and heart diseases (https://rdcu.be/d9eY7). It maps out relationships between medical data, making it easier to uncover new insights and potential treatments.

### The Knowledge Graph: 

Think of this tool as a big web of connections:

- **Nodes** are key players like genes, diseases, and medications.
- **Edges** are the links between them, showing how they're related.

By following these connections, we can discover new insights into heart disease.

### Our Data Sources

We pull information from top medical databases:

1. **GWAS Catalog**
   - A collection of genome-wide association studies (GWAS) that identify genetic variants linked to diseases.
2. **WikiPathways**
   - A database of biological pathways curated by the scientific community.
3. **Open Targets Platform**
   - A research platform that connects genetic data with disease associations and drug targets.
4. **Bgee Database**
   - A curated database of gene expression in various tissues and conditions.
## Fetching Cardiovascular-Related Data

To extract relevant cardiovascular data from these sources:
- **Filter GWAS Catalog** for heart disease-related genetic associations.
- **Use WikiPathways** to identify pathways linked to heart function and disease.
- **Query Open Targets** to find genes with known drug interactions for heart disease treatment.
- **Leverage Bgee** to analyze gene expression patterns specific to cardiovascular tissues.

## Technical Approach: Fetching Data with Python

### Fetching Data from GWAS Catalog
```python
import requests
import pandas as pd

def fetch_gwas_cardio_data():
    url = "https://www.ebi.ac.uk/gwas/rest/api/studies"
    params = {"diseaseTrait": "cardiovascular"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data["_embedded"]["studies"])
    return None
```

### Extracting Pathways from WikiPathways
```python
import requests

def fetch_wikipathways_cardio():
    url = "https://webservice.wikipathways.org/findPathwaysByText"
    params = {"query": "cardiovascular", "format": "json"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["pathways"]
    return None
```

### Querying Open Targets for Cardiovascular Disease Data
```python
import requests

def fetch_open_targets_cardio():
    url = "https://api.platform.opentargets.org/api/v4/graphql"
    query = """
    {
      disease(efoId: "EFO_0000319") {
        associatedTargets {
          rows {
            target {
              id
              approvedSymbol
            }
            score
          }
        }
      }
    }
    """
    response = requests.post(url, json={"query": query})
    if response.status_code == 200:
        return response.json()["data"]["disease"]["associatedTargets"]["rows"]
    return None
```

### Retrieving Gene Expression Data from Bgee
```python
import requests

def fetch_bgee_cardio():
    url = "https://bgee.org/api/geneExpression"
    params = {"organ": "heart"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["expressions"]
    return None
```

## Key Features

1. **Interactive Map**
   - See the full network of connections.
   - Zoom in for more detail.

2. **Smart Analysis**
   - Identify key genes linked to heart disease.
   - Find new treatment options.
   - Detect patterns that might be missed otherwise.

3. **Easy Search**
   - Look up genes or heart conditions instantly.
   - Follow the paths between them.
   - Save and share your findings.

4. **Graph Analysis**
   - Finds important connections.
   - Predicts new links that can reveal hidden relationships.

## License

MIT
