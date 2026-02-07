workspace {

    !identifiers hierarchical

    model {

        u = person "User"

        llm = softwareSystem "LLM" {
            description "Large Language Model API (e.g OpenAI, Anthropic, etc.)"
            c_api = container "Chat API"
            e_api = container "Embeddings API"
        }
        
        ss = softwareSystem "RAG System" {

            vb = container "Vector Database" {
                technology "Qdrant, ..."
                tags "Database"
            }

            app = container "Application" {
                technology "Python+Langchain"
                cli = component "Command Line Interface" {
                    !docs cli.md
                }

                illm = component "LLM Interface" {
                    !docs illm.md
                }

                ing = component "Data Ingestion" {
                    !docs ing.md
                }

                idb = component "Vector Database Interface" {
                }

                ing -> idb "stores"
                illm -> idb "retrieves"
                cli -> ing "stores"
                cli -> illm "uses"

            }

            app.illm -> llm.c_api "prompts / responses"
            app.ing -> llm.e_api "embeddings"
            app.idb -> vb "stores / retrieves"
        }

        u -> ss.app.cli "prompts"
    }

    views {
        systemContext ss {
            include *
            autolayout lr
        }

        container llm {
            include *
            autolayout lr
        } 

        container ss "rag" {
            include *
            autolayout lr
        }

        component ss.app "app_component" {
            include *
            autolayout lr
        }

        dynamic ss.app "app_store" {
            u -> ss.app.cli "stores"
            ss.app.cli -> ss.app.ing "uses"
            ss.app.ing -> llm.e_api "embeddings"
            ss.app.ing -> ss.app.idb "stores"
            autolayout lr
        }

        dynamic ss.app "app_prompt" {
            u -> ss.app.cli "prompts"
            ss.app.cli -> ss.app.illm "prompts"
            ss.app.illm -> llm.c_api "prompts / responses"
            ss.app.illm -> ss.app.idb "retrieves"
            ss.app.idb -> ss.vb "retrieves"
            autolayout lr
        }

        styles {
            element "Element" {
                background "#08427b"
                stroke #ffffff
                shape roundedBox
            }

            element "Component" {
                background "#1168bd"
                shape component
            }

            element "Software System" {
                background "#1168bd"
            }

            element "Database" {
                background "#036374"
                shape cylinder
            }
            element "Person" {
                shape person
            }
        }
    }
    
}
