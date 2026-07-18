export interface AnalysisStep {
  id: number;
  title: string;
}

export const analysisSteps: AnalysisStep[] = [
  {
    id: 1,
    title: "Search Filters",
  },
  {
    id: 2,
    title: "Additional Info",
  },
  {
    id: 3,
    title: "Review",
  },
  {
    id: 4,
    title: "Analysis",
  },
];