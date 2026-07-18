export interface TierOption {
  id: string;
  label: string;
}

export const tierOptions: TierOption[] = [
  {
    id: "all",
    label: "All",
  },
  {
    id: "web",
    label: "Web",
  },
  {
    id: "db",
    label: "DB",
  },
  {
    id: "telephony",
    label: "Telephony",
  },
];