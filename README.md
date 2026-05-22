# LexmarkScraper
Revisión de estados para impresoras Lexmark según la IP y modelo
## Lenguaje
Se hace uso de Python como único lenguaje de código.
## Modelos
Este repositorio contiene las consultas necesarias para la revisión de estatus de los siguientes modelos de impresoras:
- MX632adwe
- MS632dwe
- MX722adhe
- CX532adwe
- CX922de


## Data
La data que se puede obtener de cada modelo, variará según el modelo y será la siguiente:

### MX632adwe - MS632dwe - MX722adhe
- Black Cartridge
- Black Imaging Unit
- Maintenance Kit Information

### CX532adwe
- Cyan Cartridge
- Magenta Cartridge
- Yellow Cartridge
- Black Cartridge
- Imaging Kit
- Maintenance Kit Information
- Waste Toner Bottle

### CX922de
- Cyan Cartridge
- Magenta Cartridge
- Yellow Cartridge
- Black Cartridge
- Cyan Photoconductor
- Magenta Photoconductor
- Yellow Photoconductor
- Black Photoconductor
- Black Developer
- Color Developer Kit (CMY)
- Maintenance Kit Information
- 200K HCF Maintenance Kit
- 200K MPF Maintenance Kit
- Waste Toner Bottle
- Fuser

## Supply status levels
En la lectura de los outputs, aparecerán los estatus de las unidades de cada impresora. En muchas ocasiones, no se mostrará un número exacto, sino que se mostrará un mensaje de estatus como "Low" o "Replace". Esto servirá posteriormente para procesar la data y determinar qué impresoras requieren atención. Actualmente solo se tendrá el código para generar un output de tipo Excel para leer la información de cada impresora. El proyecto final buscará mostrar solo las impresoras que requieran atención debido al bajo nivel de cartucho, kit de mantenimiento u otros, según corresponda.

Los ejemplos de nivel de estatus son los siguientes:
### Black Cartridge
| Status      | Level    | Behavior  |
| ---------- | -- | ---------------- |
| Nearly Low | 30 | None             |
| Low        | 20 | Warning          |
| Very Low   |  7 | No changes       |
| Replace    |    | Continuable stop |

### Black Imaging Unit
| Status      | Level    | Behavior  |
| ---------- | -- | ---------------- |
| Nearly Low | 10 | None             |
| Low        |  5 | Warning          |
| Very Low   |  1 | No changes       |
| Replace    |    | Continuable stop |

### Maintance Kit Information
| Status    | Level |   Behavior     |
| ---------- | -- | ---------------- |
| Nearly Low | 10 | None             |
| Low        |  5 | Warning          |
| Very Low   |  1 | No changes       |
| Replace    |    | Continuable stop |

