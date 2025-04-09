# loterias-app-core

# **Documentação do Projeto**
## **1. Descrição Geral**
Este projeto se trata de uma função Lambda em Python projetada para interagir com uma API (possivelmente chamada de "Loterias API"), processar entradas de eventos, mapear dados e realizar cálculos relacionados a jogos de loteria com base em números sorteados. Além disso, os resultados finais são publicados por meio do método `publish`.
O principal objetivo é validar os números sorteados a partir da API de Loterias com apostas realizadas pelos usuários e retornar uma lista com os resultados dos jogos, incluindo a quantidade de acertos por jogo.
## **2. Configurações do Projeto**
### **2.1 Variáveis de Ambiente**
O projeto utiliza variáveis de ambiente para definir configurações essenciais:
- `BASE_URL`: URL base da API de Loterias.
- `TOKEN`: Token utilizado para autenticação na API.

### **2.2 Bibliotecas Utilizadas**
O código utiliza as seguintes bibliotecas:
- **`requests`**: Para realizar chamadas HTTP à API de Loterias.
- **`os`**: Para acessar variáveis de ambiente do sistema.
- **Componentes Internos**:
    - `mapper.map_dto.map_object`: Função para mapear as entradas (`event`) em objetos processáveis.
    - `helper.publisher.publish`: Função responsável por publicar os resultados processados.

## **3. Estrutura da Função Lambda**
### **3.1 Entradas**
- **`event`**: Objeto de entrada contendo dados dos jogos a serem processados.
    - Contém informações como o número do concurso e os jogos realizados por cada usuário.

- **`context`**: Informações sobre o contexto de execução (não utilizado diretamente no código).

### **3.2 Fluxo da Função**
1. **Recebimento dos dados de entrada:**
    - Imprime os dados recebidos de `event` e `context` para depuração.

2. **Mapeamento dos objetos:**
    - Utiliza a função `map_object` para processar e formatar as informações de entrada em uma estrutura adequada.
    - O resultado é uma lista de objetos com informações relacionadas a loterias.

3. **Processamento de cada item:**
    - Para cada item da lista mapeada:
        - Preparar o payload com informações como: nome da loteria, token de autenticação e número do concurso.
        - Realizar uma requisição `GET` para a API de Loterias.
        - Validar a resposta:
            - Verificar se o número de concurso da resposta coincide com o número enviado.
            - Caso contrário, lançar uma exceção indicando que o sorteio ainda não foi concluído.

        - Extrair as dezenas sorteadas e formatá-las para remover zeros à esquerda.

4. **Cálculo de acertos:**
    - Comparar os números sorteados com os números correspondentes de cada jogo do usuário (`games_user`).
    - Registrar o total de acertos por jogo e armazenar os resultados no formato:
``` json
     {
         "jogo": <Jogos Individuais>,
         "concurso": <Número do Concurso>,
         "Dezenas Sorteadas": <Dezenas da API>,
         "Total de acertos": <Total de Números Iguais>
     }
```
1. **Publicação dos Resultados:**
    - Enviar a lista de resultados finais usando a função `publish`.

2. **Retorno Final:**
    - Em caso de sucesso: Retorna um objeto JSON com o código `200`.
    - Em caso de falha: Retorna o código `500` com a mensagem da exceção.

## **4. Arquitetura Interna**
### **4.1 Componentes**
1. **Função Principal (`lambda_handler`)**:
    - Responsável por controlar o fluxo de execução, incluindo chamadas para mapeamento, API, cálculo dos resultados e publicação.

2. **Funções Auxiliares/Dependências:**
    - `map_object` (via `mapper.map_dto`): Mapeia o evento para um formato pré-definido.
    - `publish` (via `helper.publisher`): Publica os resultados dos jogos processados.

### **4.2 Organização do Código**
O código está escrito no formato de script Python, dividido de forma simples em:
- Importações de bibliotecas e módulos.
- Declarações de variáveis globais (configurações via `os.getenv`).
- Definição da função principal.

## **5. Detalhes Técnicos**
### **5.1 Requisição à API**
A comunicação com a API de Loterias é feita com uma requisição HTTP `GET`. Estrutura do payload enviado:
``` python
{
    "loteria": i["loteria"],
    "token": token,
    "concurso": i["concurso"]
}
```
Os dados importantes obtidos da API incluem:
- `numero_concurso`: Usado para validação.
- `dezenas`: Números sorteados pelo sistema.

### **5.2 Tratamento de Exceções**
Em caso de erros durante o processo (ex.: números do concurso indisponíveis ou erros da API), uma exceção é lançada e tratada retornando:
``` json
{
    "code": 500,
    "message": "<Mensagem do Erro>"
}
```
### **5.3 Publicação**
A lista final, contendo o resultado de cada jogo, é enviada pela função `publish`. O formato dos dados publicados é:
``` json
[
    {
        "jogo": <Jogos do Usuário>,
        "concurso": <Número do Concurso>,
        "Dezenas Sorteadas": <Números Sorteados>,
        "Total de acertos": <Quantidade de Acertos>
    },
    ...
]
```
## **6. Testes**
### **6.1 Casos de Teste Sugeridos**
1. **Entrada Válida**:
    - Evento com jogos e concursos válidos.
    - API retorna as dezenas corretas.
    - Verificar se o retorno inclui os acertos corretos.

2. **Erro na API**:
    - Quando o número do concurso não está disponível na API.
    - Verificar se a exceção é tratada corretamente.

3. **Formato Inválido no Evento**:
    - Simular eventos mal formatados para confirmar comportamento.

4. **Teste com Múltiplos Jogos**:
    - Validar o comportamento com mais de um jogo simultâneo no evento.

## **7. Possíveis Melhorias**
- Implementar logging estruturado em vez de `print` para melhor rastreamento.
- Adicionar mais validações nas entradas (ex.: validação do JSON recebido).
- Adicionar testes unitários para verificar funções críticas como `map_object` e `publish`.
- Adotar uma abordagem mais robusta para gerenciar erros no consumo da API (ex.: re-tentativas).
