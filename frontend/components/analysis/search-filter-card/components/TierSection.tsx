import { Badge } from "@/components/ui/badge";

const tiers = [
  "TIER 1",
  "TIER 2",
  "TIER 3",
];

export default function TierSection() {
  return (
    <div>

      <h3 className="mb-4 text-lg font-semibold">
        Tier
      </h3>

      <div className="flex gap-3">

        {tiers.map((tier) => (
          <Badge
            key={tier}
            className="cursor-pointer px-5 py-2"
          >
            {tier}
          </Badge>
        ))}

      </div>

    </div>
  );
}