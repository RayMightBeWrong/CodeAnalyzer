# CodeAnalyzer
Este projeto consiste num analisador de código de uma LPI (Linguagem de Programação Imperativa) capaz de gerar uma página HTML com diversas informações sobre o programa processado, tais como indicar erros e avisos anotados no código, as variáveis usadas e os seus tipos, instruções usadas, entre outras.

[Gramática LPI](https://github.com/RayMightBeWrong/CodeAnalyzer/blob/main/CodeAnalyzer/grammar.py)

### EXECUTAR O PROGRAMA
```
python3 CodeAnalyzer input_file [-o output_file]
```

### EXEMPLOS DA LINGUAGEM DESENVOLVIDA

##### DECLARAÇÕES E ATRIBUIÇÕES
```
int i = 5;
bool b = true;
string s = "example string";
int[3] v = [1,2,3];
i = v[2];
v[1] = i * (4 + v[1]);
b = v[1] == 4 or false;
list l = {"abc", true, 10};
tuple t = (15, "xyz")
```

##### INSTRUÇÕES

```
if i < 20 { string s = "i é menor que 20"; }
elif (i < 40) { string s = "i é menor que 40"; }
else { string s = "i é maior ou igual a 40"; }

while (i < 100) { i = i + 1; }

do { i = random(100, 200); } while i < 150

for var in [1,2,3] {}
for val in values {}
for d in [1 -> 10] {}

switch i
case 5 {}
case 10 {}
default {}
```

##### DEFINIÇÃO DE FUNÇÕES
```
def sum(arg1, arg2){
    return arg1 + arg2;
}
```

### EXEMPLO DO HTML GERADO
<img src="https://i.imgur.com/CC5AzMV.png"  width="600">
<img src="https://i.imgur.com/TM8RonJ.png"  width="600">
<img src="https://i.imgur.com/pWQBmdX.png"  width="600">
<img src="https://i.imgur.com/xNJ1igg.png"  width="600">
