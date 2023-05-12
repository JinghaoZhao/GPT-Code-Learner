# Knowledge Base

GPT-Code-Learner supports using a knowledge base to answer questions. By default, it will use the codebase as the knowledge base. You can preload documents or provide URLs as background knowledge for the repo you want to learned.

The knowledge base is powered by a vector database. The local version uses [FAISS](https://github.com/facebookresearch/faiss), while the cloud version utilizes [Supabase](https://app.supabase.com/).

## Supabase Setup

For the Supabase version, create a Supabase account and project at https://app.supabase.com/sign-in. Next, add your Supabase URL and key to the `.env` file. You can find them in the portal under Project/API.

```
SUPABASE_URL=https://xxxxxx.supabase.co
SUPABASE_KEY=xxxxxx
```

Create the default document table using the following SQL, which follows the format of the [langchain example](https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/supabase.html).

```postgresql
-- Enable the pgvector extension to work with embedding vectors
create extension vector;

-- Create a table to store your documents
create table documents (
id bigserial primary key,
content text, -- corresponds to Document.pageContent
metadata jsonb, -- corresponds to Document.metadata
embedding vector(1536) -- 1536 works for OpenAI embeddings, change if needed
);

CREATE FUNCTION match_documents(query_embedding vector(1536), match_count int)
   RETURNS TABLE(
       id bigint,
       content text,
       metadata jsonb,
       -- we return matched vectors to enable maximal marginal relevance searches
       embedding vector(1536),
       similarity float)
   LANGUAGE plpgsql
   AS $$
   # variable_conflict use_column
BEGIN
   RETURN query
   SELECT
       id,
       content,
       metadata,
       embedding,
       1 -(documents.embedding <=> query_embedding) AS similarity
   FROM
       documents
   ORDER BY
       documents.embedding <=> query_embedding
   LIMIT match_count;
END;
$$;
```

The [knowledge_base.py](..%2Fknowledge_base.py) provides examples of how to use the knowledge base.