// Catchall file for one-off constants

// Screens LESS THAN 910px wide swap to a layout optimized for smaller devices
// For now this includes both small screens and mobile
export const DESKTOP_BREAKPOINT = 910;

// CDN points to blob storage here: https://bescienceswebsite.blob.core.windows.net
export const BLOB_STORAGE_URL = 'https://bescdn.breakthroughenergy.org';
// Our US Test system paper is also on ieee here: https://ieeexplore.ieee.org/document/9281850
export const US_TEST_SYSTEM_PAPER_URL = BLOB_STORAGE_URL + '/publications/US_Test_System_with_High_Spatial_and_Temporal_Resolution.pdf';
export const US_TEST_SYSTEM_DATA_URL = 'https://zenodo.org/record/3530898';
export const NREL_SEAMS_STUDY_URL = 'https://www.nrel.gov/analysis/seams.html';
export const MACRO_GRID_REPORT_URL = BLOB_STORAGE_URL + '/publications/MacroGridReport.pdf';
export const TEXAS_PDF_URL = BLOB_STORAGE_URL + '/publications/corrective_measure_assessment_of_the_2021_texas_power_outage.pdf';
export const DEMAND_FLEXIBILITY_URL = BLOB_STORAGE_URL + '/publications/How_much_demand_flexibility_could_have_spared_Texas.pdf';
export const OPEN_SOURCE_DOCS_URL = 'https://breakthrough-energy.github.io/docs/';
