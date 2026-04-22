1. acrescentar informações dos lotes condominiais (apartamento) vinculando eles aos polígonos
2. fazer o melt dos lotes que tem mais de um polígono, transformando em multipoligono
3. criar a base indexada por Setor, Quadra, Lote, Condominio, Tipo de Lote (ou seja, pelo lote em si seja apartamento ou não) - aí os lotes de apartamento herdam o zonemento do polígono do lote do condominio
4. A base final, indexada por lote, deve ter uma coluna para cada zoneamento existente. dentro dessa coluna, um número de 1 a 100 que representa a importância daqueel zoneamento (como já calculamos) para aquele lote. A soma das importancias de todas as zonas deve ser igual a 100
5. A base final deve ser nesse formato:
| Setor | Quadra | Lote | Condomínio | Tipo de Lote | ZOE | ZC | ZEU |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 001 | 015 | 0024 | 08 | F | 20 | 30 | 50 |
| 002 | 042 | 1250 | 15 | M | 10 | 80 | 10 |
| 003 | 088 | 0500 | 22 | V | 45 | 45 | 10 |
| 004 | 102 | 9999 | 40 | F | 60 | 20 | 20 |
| 005 | 067 | 0001 | 99 | M | 33 | 33 | 34 |

6. Acrescentar na base uma coluna de observações (para falar se o lote é multipoligono, etc.) e também colocar a área total do lote e a área total intersectada pelo zoneamento

Enviar também a base indexada por id do polígono para o Bruno Carano.