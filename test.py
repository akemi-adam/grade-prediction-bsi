from pandas import DataFrame, read_csv, merge
from enum import Enum

# DF de componentes
componentes: DataFrame = read_csv('componentes-curriculares-presenciais.csv', sep=';')
componentes: DataFrame = componentes[['id_componente', 'tipo_componente', 'codigo', 'nome', 'unidade_responsavel', 'curso_componente']]

# Somente alguns componentes com o código BSI estão com a informaçaõ do curso
# Aqui eu procuro os componentes com código DCT/BSI e atualizo essa informação
componentes['codigo'] = componentes['codigo'].astype(str)

# DF de turmas
turmas: DataFrame = read_csv('turmas-2017.1.csv', sep=';')

# DF de matriculas
matriculas: DataFrame = read_csv('matricula-componente-20171.csv', sep=';')


# Faz merge/join entre data frames
df_temp: DataFrame = merge(componentes, turmas, left_on='id_componente', right_on='id_componente_curricular')
df_temp = merge(df_temp, matriculas, on='id_turma')

df_filtrado: DataFrame = df_temp[(
    (df_temp['codigo'].str.startswith(('DCT', 'BSI'))) &
    (df_temp['tipo_componente'] == 'DISCIPLINA')
)]

# Enum de status possíveis da matrícula
# Validar se existe status de somente reprovado por falta
class StatusMatricula(Enum):
    APROVADO = ('APROVADO', 'Discente foi aprovado')
    APROVADO_POR_NOTA = ('APROVADO POR NOTA', 'Discente aprovado por nota')
    CANCELADO = ('CANCELADO', 'Matrícula cancelada')
    DESISTENCIA = ('DESISTENCIA', 'Discente desistiu do componente curricular')
    EXCLUIDA = ('EXCLUIDA', 'Matrícula excluída')
    INDEFERIDO = ('INDEFERIDO', 'Processamento da matrícula do discente foi indeferida')
    REPROVADO_POR_MEDIA_E_POR_FALTAS = ('REPROVADO POR MÉDIA E POR FALTAS', 'Discente foi reprovado por média e por faltas')
    REPROVADO_POR_NOTA = ('REPROVADO POR NOTA', 'Discente reprovado por nota')
    REPROVADO = ('REPROVADO', 'Discente foi reprovado')
    TRANCADO = ('TRANCADO', 'Discente trancou a matrícula do componente curricular')
    
    @classmethod
    def status_validos(cls) -> list[str]:
        return [
            cls.APROVADO.value[0],
            cls.APROVADO_POR_NOTA.value[0],
            cls.REPROVADO.value[0],
            cls.REPROVADO_POR_NOTA.value[0]
        ]


# Filtra por status válidos
df_filtrado = df_filtrado[df_filtrado['descricao'].isin(StatusMatricula.status_validos())]

df_filtrado['unidade'] = df_filtrado['unidade'].astype(int)

# Cria colunas de notas por unidade
notas_pivot = df_filtrado.pivot_table(
    index=['discente', 'id_turma'],
    columns='unidade',
    values='nota',
    aggfunc='first'
).rename(columns={
    1: 'nota_unidade_1',
    2: 'nota_unidade_2',
    3: 'nota_unidade_3'
})

df_filtrado = df_filtrado.merge(
    notas_pivot,
    on=['discente', 'id_turma'],
    how='left'
)

df_filtrado = df_filtrado.drop_duplicates(subset=['discente', 'id_turma'])

df_final = df_filtrado[
    [
        'id_componente',
        'nome',
        'id_turma',
        'ano',
        'periodo',
        'discente',
        'nota_unidade_1',
        'nota_unidade_2',
        'nota_unidade_3',
        'media_final',
        'descricao'
    ]
]

print(df_final.shape)
df_final.to_csv('final.csv')