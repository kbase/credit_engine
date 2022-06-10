
# Class: Resolvable_PID




URI: [https://kbase/credit_engine/schema/metadata/ResolvablePID](https://kbase/credit_engine/schema/metadata/ResolvablePID)


[![img](https://yuml.me/diagram/nofunky;dir:TB/class/[Dataset]++-%20resolvable_persistent_identifiers%200..*>[ResolvablePID&#124;id:string;uri:string%20%3F;description:string%20%3F;repository:string%20%3F],[Dataset])](https://yuml.me/diagram/nofunky;dir:TB/class/[Dataset]++-%20resolvable_persistent_identifiers%200..*>[ResolvablePID&#124;id:string;uri:string%20%3F;description:string%20%3F;repository:string%20%3F],[Dataset])

## Referenced by Class

 *  **None** *[➞resolvable_persistent_identifiers](dataset__resolvable_persistent_identifiers.md)*  <sub>0..\*</sub>  **[ResolvablePID](ResolvablePID.md)**

## Attributes


### Own

 * [➞id](resolvablePID__id.md)  <sub>1..1</sub>
     * Description: a CURIE (compact URI)
     * Range: [String](types/String.md)
 * [➞uri](resolvablePID__uri.md)  <sub>0..1</sub>
     * Description: URI for a resource
     * Range: [String](types/String.md)
 * [➞description](resolvablePID__description.md)  <sub>0..1</sub>
     * Description: brief description of what the ID links to
     * Range: [String](types/String.md)
 * [➞repository](resolvablePID__repository.md)  <sub>0..1</sub>
     * Description: entity within which the RPI is held
     * Range: [String](types/String.md)
