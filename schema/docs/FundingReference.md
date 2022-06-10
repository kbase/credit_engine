
# Class: FundingReference




URI: [https://kbase/credit_engine/schema/metadata/FundingReference](https://kbase/credit_engine/schema/metadata/FundingReference)


[![img](https://yuml.me/diagram/nofunky;dir:TB/class/[Dataset]++-%20funding_references%200..*>[FundingReference&#124;funder_name:string;funder_id:string%20%3F;award_id:string%20%3F;award_title:string%20%3F;award_uri:string%20%3F],[Dataset])](https://yuml.me/diagram/nofunky;dir:TB/class/[Dataset]++-%20funding_references%200..*>[FundingReference&#124;funder_name:string;funder_id:string%20%3F;award_id:string%20%3F;award_title:string%20%3F;award_uri:string%20%3F],[Dataset])

## Referenced by Class

 *  **None** *[➞funding_references](dataset__funding_references.md)*  <sub>0..\*</sub>  **[FundingReference](FundingReference.md)**

## Attributes


### Own

 * [➞funder_name](fundingReference__funder_name.md)  <sub>1..1</sub>
     * Description: human-readable funding body name
     * Range: [String](types/String.md)
 * [➞funder_id](fundingReference__funder_id.md)  <sub>0..1</sub>
     * Description: ID for the funding entity
     * Range: [String](types/String.md)
 * [➞award_id](fundingReference__award_id.md)  <sub>0..1</sub>
     * Description: code assigned by the funder to the grant or award
     * Range: [String](types/String.md)
 * [➞award_title](fundingReference__award_title.md)  <sub>0..1</sub>
     * Description: human-readable title of the grant or award
     * Range: [String](types/String.md)
 * [➞award_uri](fundingReference__award_uri.md)  <sub>0..1</sub>
     * Description: URI for the award
     * Range: [String](types/String.md)
