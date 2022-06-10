
# Class: Contributor




URI: [https://kbase/credit_engine/schema/metadata/Contributor](https://kbase/credit_engine/schema/metadata/Contributor)


[![img](https://yuml.me/diagram/nofunky;dir:TB/class/[Dataset]++-%20contributors%200..*>[Contributor&#124;orcid:string;first_name:string%20%3F;last_name:string%20%3F;full_name:string%20%3F;affiliation:string%20%3F;contributor_role:string%20%3F],[Dataset])](https://yuml.me/diagram/nofunky;dir:TB/class/[Dataset]++-%20contributors%200..*>[Contributor&#124;orcid:string;first_name:string%20%3F;last_name:string%20%3F;full_name:string%20%3F;affiliation:string%20%3F;contributor_role:string%20%3F],[Dataset])

## Referenced by Class

 *  **None** *[➞contributors](dataset__contributors.md)*  <sub>0..\*</sub>  **[Contributor](Contributor.md)**

## Attributes


### Own

 * [➞orcid](contributor__orcid.md)  <sub>1..1</sub>
     * Description: ORCID
     * Range: [String](types/String.md)
 * [➞first_name](contributor__first_name.md)  <sub>0..1</sub>
     * Description: given name
     * Range: [String](types/String.md)
 * [➞last_name](contributor__last_name.md)  <sub>0..1</sub>
     * Description: family name
     * Range: [String](types/String.md)
 * [➞full_name](contributor__full_name.md)  <sub>0..1</sub>
     * Description: Full name of the contributor
     * Range: [String](types/String.md)
 * [➞affiliation](contributor__affiliation.md)  <sub>0..1</sub>
     * Description: organisation that the contributor is associated with
     * Range: [String](types/String.md)
 * [➞contributor_role](contributor__contributor_role.md)  <sub>0..1</sub>
     * Description: should be a term from either CRedIT or DataCite
     * Range: [String](types/String.md)
