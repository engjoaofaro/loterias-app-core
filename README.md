# loterias-app-core

Lambda (Python) que é o **núcleo de apuração** do **Loterias Sim**: recebe as apostas
(via Step Functions, no formato do DynamoDB), consulta o resultado oficial na API de
loterias, **confere quantos números cada jogo acertou** e publica o resultado no SNS
(e-mail ao usuário).

> Função Lambda implantada: `loterias-core`.
> Parte do ecossistema **Loterias Sim** — visão geral em [Arquitetura](#arquitetura-e-fluxo).

---

## Visão geral

| Item | Valor |
|------|-------|
| Runtime | Python 3.9+ |
| Handler | `lambda_function.lambda_handler` |
| Invocação | Task de uma **AWS Step Functions** (agendada pelo `loterias-app-validator`) |
| Entrada | Itens no formato AttributeValue do DynamoDB (`{"N":...}`, `{"S":...}`, `{"L":...}`) |
| Saída | Publica no **SNS** (`TOPIC_ARN`) e retorna `{code:200}`/`{code:500}` para o fluxo |
| Dependências | `requests~=2.32.3`, `boto3~=1.26.105` |

### Loterias suportadas (`gameType`)
| Código | Loteria |
|:------:|---------|
| 1 | Mega-Sena |
| 2 | Lotofácil |
| 3 | Lotomania |

---

## Estrutura

```
loterias-app-core/
├── lambda_function.py     # Handler: mapeia → consulta API → confere acertos → publica
├── mapper/
│   └── map_dto.py         # map_object(event): DynamoDB AttributeValue → dicts normalizados
└── helper/
    └── publisher.py       # publish(message): SNS publish no TOPIC_ARN (Subject "RESULTADO LOTERIA")
```

---

## Fluxo do handler

1. **Mapeamento** — `map_object(event)` percorre `event['Items']`, traduz `gameType`
   (1/2/3 → `megasena`/`lotofacil`/`lotomania`) e extrai `voucher`, `lotteryNumber`
   (concurso), `email` e `games` (listas de dezenas).
2. **Consulta à API** — para cada item, `GET {BASE_URL}?loteria&token&concurso`.
3. **Validação** — se `numero_concurso` da API ≠ `concurso` solicitado, lança exceção
   ("sorteio ainda não efetuado").
4. **Conferência** — remove zeros à esquerda das dezenas e conta os acertos de cada
   jogo do usuário.
5. **Publicação** — `publish(final_list)` no SNS.
6. **Retorno** — `{ "code": 200 }` (sucesso) ou `{ "code": 500, "message": "..." }`
   (erro) para o próximo estado da Step Function.

### Entrada (event)
```json
{
  "Items": [
    {
      "gameType": {"N": "1"},
      "voucher": {"S": "TXN_123"},
      "lotteryNumber": {"N": "2890"},
      "email": {"S": "user@example.com"},
      "games": {"L": [ {"L": [ {"N":"5"}, {"N":"12"}, {"N":"45"} ]} ]}
    }
  ]
}
```

### Resultado publicado (SNS)
```json
[
  {
    "jogo": [ {"N":"5"}, {"N":"12"}, {"N":"45"} ],
    "concurso": "2890",
    "Dezenas Sorteadas": ["05","12","45","67","78","90"],
    "Total de acertos": 3
  }
]
```

---

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `BASE_URL` | URL base da API de loterias |
| `TOKEN` | Token de autenticação da API |
| `TOPIC_ARN` | ARN do tópico SNS onde os resultados são publicados |

---

## Permissões (IAM)

A role precisa apenas de `sns:Publish` no `TOPIC_ARN` (os dados das apostas chegam
prontos no evento da Step Functions; não há acesso direto ao DynamoDB aqui).

---

## Deploy

```bash
pip install -r requirements.txt -t build/
cp -r lambda_function.py mapper/ helper/ build/
( cd build && zip -r ../function.zip . )
aws lambda update-function-code --function-name loterias-core \
  --zip-file fileb://function.zip --region sa-east-1
```

Recomenda-se timeout ≥ 30 s (faz chamadas HTTP externas).

---

## Arquitetura e fluxo

```
loterias-app-validator ─► EventBridge Scheduler ─► Step Functions
                                                        │ (Task)
                                                        ▼
                                                 loterias-app-core ─► API Caixa
                                                        │
                                                        ▼
                                                   SNS ─► e-mail do usuário
```

Esta Lambda é uma **Task** dentro da máquina de estados (definida fora deste repo, em
IaC). O retorno `code` (200/500) direciona o próximo estado.

---

## Testes sugeridos

1. **Entrada válida** — jogos/concurso válidos; conferir contagem de acertos.
2. **Erro na API** — concurso ainda não sorteado; conferir tratamento da exceção.
3. **Evento mal formatado** — confirmar comportamento.
4. **Múltiplos jogos** — validar laço de conferência.

---

## Pontos de atenção e melhorias

- 🔢 **Conferência O(n·m·k)** (laço triplo) — para muitos jogos, otimizar usando
  `set(dezenas_sorteadas)` e contagem por interseção.
- ⚠️ **Sem retry/timeout explícito** na chamada HTTP; `except Exception` genérico.
  Separar erros de API, validação e SNS.
- ⚠️ **`publish()` sem tratamento de erro:** se o SNS falhar, ainda assim a Lambda
  pode retornar 200. Tratar e refletir no `code`.
- 🪵 Trocar `print` por logging estruturado.
- 🔐 Mover `TOKEN` para Secrets Manager/SSM.
- 🧪 Adicionar testes unitários para `map_object` e a lógica de acertos.
- 📊 Comparação de strings (`x['N'] == dezena`) é frágil a tipos/zero-padding —
  normalizar para `int` dos dois lados.
