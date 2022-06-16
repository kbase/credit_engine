
# Class: Dataset




URI: [https://kbase/credit_engine/schema/metadata/Dataset](https://kbase/credit_engine/schema/metadata/Dataset)


[![img](https://yuml.me/diagram/nofunky;dir:TB/class/[ResolvablePID],[FundingReference],[FundingReference]<funding_references%200..*-++[Dataset&#124;titles:string%20*;version:string%20%3F;submission_date:string%20%3F;access_date:string%20%3F],[ResolvablePID]<resolvable_persistent_identifiers%200..*-++[Dataset],[Contributor]<contributors%200..*-++[Dataset],[Contributor])](https://yuml.me/diagram/nofunky;dir:TB/class/[ResolvablePID],[FundingReference],[FundingReference]<funding_references%200..*-++[Dataset&#124;titles:string%20*;version:string%20%3F;submission_date:string%20%3F;access_date:string%20%3F],[ResolvablePID]<resolvable_persistent_identifiers%200..*-++[Dataset],[Contributor]<contributors%200..*-++[Dataset],[Contributor])

## Attributes


### Own

 * [➞titles](dataset__titles.md)  <sub>0..\*</sub>
     * Description: formal title(s) of the data set
     * Range: [String](types/String.md)
 * [➞version](dataset__version.md)  <sub>0..1</sub>
     * Description: dataset version (if available)
     * Range: [String](types/String.md)
 * [➞submission_date](dataset__submission_date.md)  <sub>0..1</sub>
     * Description: date of submission to repository (if available)
     * Range: [String](types/String.md)
 * [➞access_date](dataset__access_date.md)  <sub>0..1</sub>
     * Description: for unversioned datasets, the date of access of the dataset
     * Range: [String](types/String.md)
 * [➞contributors](dataset__contributors.md)  <sub>0..\*</sub>
     * Description: people and/or organisations responsible for generating the dataset
     * Range: [Contributor](Contributor.md)
 * [➞resolvable_persistent_identifiers](dataset__resolvable_persistent_identifiers.md)  <sub>0..\*</sub>
     * Description: unique IDs used to access the dataset or any ancestral datasets
     * Range: [ResolvablePID](ResolvablePID.md)
 * [➞funding_references](dataset__funding_references.md)  <sub>0..\*</sub>
     * Description: funding sources for the dataset
     * Range: [FundingReference](FundingReference.md)
