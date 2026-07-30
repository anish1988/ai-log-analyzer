export interface MatchedLine {
    server: string;
    file: string;
    file_id: string;
    line_number: number;
    raw: string;
    matched_filters: string[];
  }
  
  export interface SearchMeta {
    leadid: string;
    outbound: string;
  }
  
  export interface FileResult {
    file_id: string;
    file_label: string;
    server: string;
    searched_file: string;
    matched_count: number;
    meta: SearchMeta;
    lines: MatchedLine[];
  }
  
  export interface SearchSummary {
    total_matches: number;
    files_matched: number;
    servers: number;
  }
  
  export interface PreviewSessionResponse {
    summary: SearchSummary;
    results: FileResult[];
  }