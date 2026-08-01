# Baseline Validation Report

| check                                                           | status | detail                                                                       |
| --------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------- |
| ES.v.0 daily pipeline_version                                   | PASS   | ['boundary_corrected_v1']                                                    |
| ES.v.0 daily executable LH                                      | PASS   | r_LH_executable column present                                               |
| ES.v.0 kept same-contract rows                                  | PASS   | kept rows have same_instrument_as_prev=True                                  |
| ES.v.0 regression pipeline_version                              | PASS   | {'boundary_corrected_v1'}                                                    |
| ES.v.0 OOS pipeline_version                                     | PASS   | {'boundary_corrected_v1'}                                                    |
| NQ.v.0 daily pipeline_version                                   | PASS   | ['boundary_corrected_v1']                                                    |
| NQ.v.0 daily executable LH                                      | PASS   | r_LH_executable column present                                               |
| NQ.v.0 kept same-contract rows                                  | PASS   | kept rows have same_instrument_as_prev=True                                  |
| NQ.v.0 regression pipeline_version                              | PASS   | {'boundary_corrected_v1'}                                                    |
| NQ.v.0 OOS pipeline_version                                     | PASS   | {'boundary_corrected_v1'}                                                    |
| GC.v.0 daily pipeline_version                                   | PASS   | ['boundary_corrected_v1']                                                    |
| GC.v.0 daily executable LH                                      | PASS   | r_LH_executable column present                                               |
| GC.v.0 kept same-contract rows                                  | PASS   | kept rows have same_instrument_as_prev=True                                  |
| GC.v.0 regression pipeline_version                              | PASS   | {'boundary_corrected_v1'}                                                    |
| GC.v.0 OOS pipeline_version                                     | PASS   | {'boundary_corrected_v1'}                                                    |
| CL.v.0 daily pipeline_version                                   | PASS   | ['boundary_corrected_v1']                                                    |
| CL.v.0 daily executable LH                                      | PASS   | r_LH_executable column present                                               |
| CL.v.0 kept same-contract rows                                  | PASS   | kept rows have same_instrument_as_prev=True                                  |
| CL.v.0 regression pipeline_version                              | PASS   | {'boundary_corrected_v1'}                                                    |
| CL.v.0 OOS pipeline_version                                     | PASS   | {'boundary_corrected_v1'}                                                    |
| ZN.v.0 daily pipeline_version                                   | PASS   | ['boundary_corrected_v1']                                                    |
| ZN.v.0 daily executable LH                                      | PASS   | r_LH_executable column present                                               |
| ZN.v.0 kept same-contract rows                                  | PASS   | kept rows have same_instrument_as_prev=True                                  |
| ZN.v.0 regression pipeline_version                              | PASS   | {'boundary_corrected_v1'}                                                    |
| ZN.v.0 OOS pipeline_version                                     | PASS   | {'boundary_corrected_v1'}                                                    |
| 6E.v.0 daily pipeline_version                                   | PASS   | ['boundary_corrected_v1']                                                    |
| 6E.v.0 daily executable LH                                      | PASS   | r_LH_executable column present                                               |
| 6E.v.0 kept same-contract rows                                  | PASS   | kept rows have same_instrument_as_prev=True                                  |
| 6E.v.0 regression pipeline_version                              | PASS   | {'boundary_corrected_v1'}                                                    |
| 6E.v.0 OOS pipeline_version                                     | PASS   | {'boundary_corrected_v1'}                                                    |
| reports/final_baseline_summary_zh.md p display                  | PASS   | Markdown p-values below 0.001 display as p<0.001                             |
| reports/final_baseline_summary_en.md p display                  | PASS   | Markdown p-values below 0.001 display as p<0.001                             |
| reports/core_rerun_summary_boundary_corrected_v1.md p display   | PASS   | Markdown p-values below 0.001 display as p<0.001                             |
| README final baseline references                                | PASS   | README points readers to frozen boundary_corrected_v1 summaries              |
| README excludes invalid v0 headline numbers                     | PASS   | README does not cite invalid_boundary_v0 numeric results in main conclusions |
| .gitignore contains data/raw/                                   | PASS   | data/raw/                                                                    |
| .gitignore contains data/processed/                             | PASS   | data/processed/                                                              |
| .gitignore contains .env                                        | PASS   | .env                                                                         |
| .gitignore contains .env.*                                      | PASS   | .env.*                                                                       |
| .gitignore contains *.dbn                                       | PASS   | *.dbn                                                                        |
| .gitignore contains *.parquet                                   | PASS   | *.parquet                                                                    |
| .gitignore contains reports/archive/invalid_boundary_v0/tables/ | PASS   | reports/archive/invalid_boundary_v0/tables/                                  |
| manifest pipeline_version                                       | PASS   | all manifest rows boundary_corrected_v1                                      |