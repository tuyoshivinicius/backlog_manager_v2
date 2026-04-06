# epic Input Template

Use este template para estruturar a descricao da epic antes de passar ao `/speckit.specify`.
Preencha as secoes relevantes, remova as que nao se aplicam, e cole o conteudo como argumento do comando.

> **Regra de ouro**: descreva O QUE o usuario precisa e POR QUE — nunca COMO implementar.
> Nao mencione frameworks, linguagens, APIs, bancos de dados ou infraestrutura.

---

## Titulo

<!-- Nome curto e descritivo da epic (2-5 palavras) -->

[Nome da epic]

## Descricao

<!-- O que e esta epic e por que ela importa? Qual problema resolve ou valor entrega? -->

[Descreva a epic em 2-4 frases focando no valor de negocio]

## Atores

<!-- Quem interage com esta epic? Liste os tipos de usuario envolvidos. -->

- **[Ator 1]**: [breve descricao do papel e motivacao]
- **[Ator 2]**: [breve descricao do papel e motivacao]

## Fluxos Principais

<!-- Descreva as acoes que os atores realizam, na ordem em que acontecem. -->

1. [Ator] faz [acao] para [objetivo]
2. O sistema [responde/apresenta/valida] [resultado]
3. [Ator] pode [proxima acao]

## Regras de Negocio

<!-- Restricoes, validacoes ou comportamentos obrigatorios que a epic deve respeitar. -->

- [Regra 1: ex. "Apenas administradores podem aprovar solicitacoes"]
- [Regra 2: ex. "O limite maximo por operacao e de R$ 5.000"]

## Escopo

<!-- Defina limites claros para evitar ambiguidade. -->

**Inclui**:
- [Funcionalidade que faz parte desta epic]
- [Outro item incluido]

**Nao inclui**:
- [Funcionalidade explicitamente fora do escopo]
- [Outro item excluido]

## Criterios de Sucesso

<!-- Como saber se a epic foi bem-sucedida? Use metricas mensuráveis e agnósticas de tecnologia. -->

- [Metrica 1: ex. "Usuarios completam o cadastro em menos de 2 minutos"]
- [Metrica 2: ex. "Taxa de erro no fluxo principal abaixo de 5%"]
- [Metrica 3: ex. "90% dos usuarios concluem a tarefa na primeira tentativa"]

---

## Exemplo Preenchido

> Para referencia — remova esta secao antes de usar.

**Titulo**: Inicializacao do Projeto

**Descricao**: O framework deve oferecer um comando de inicializacao que cria a estrutura de diretorios do projeto, gera o arquivo de constituicao a partir de um template interativo, e configura o engine de especificacao. O objetivo e que novos projetos comecem com uma base padronizada e governada por principios explicitos.

**Atores**:
- **Desenvolvedor**: inicia um novo projeto e quer uma estrutura pronta para uso

**Fluxos Principais**:
1. Desenvolvedor executa o comando de inicializacao
2. Sistema apresenta opcoes de preset de principios ou permite definicao customizada
3. Desenvolvedor escolhe preset ou define principios
4. Sistema cria estrutura de diretorios e arquivos de configuracao
5. Desenvolvedor confirma a configuracao gerada

**Regras de Negocio**:
- A inicializacao deve ser idempotente — executar novamente nao sobrescreve configuracoes existentes sem confirmacao explicita
- Presets devem ser extensiveis — o usuario pode adicionar principios apos escolher um preset

**Escopo**:
- **Inclui**: criacao de diretorios, geracao de constituicao, configuracao do engine
- **Nao inclui**: integracao com CI/CD, configuracao de deploy

**Criterios de Sucesso**:
- Novo projeto fica funcional e pronto para especificacao em menos de 5 minutos
- 100% dos arquivos obrigatorios sao gerados sem erro
- Re-execucao do comando em projeto existente nao causa perda de dados
