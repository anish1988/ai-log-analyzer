import { Input } from "@/components/ui/input";

export default function DateRangeSection() {
  return (
    <div>

      <h3 className="mb-4 text-lg font-semibold">
        Date Range
      </h3>

      <div className="grid grid-cols-2 gap-6">

        <Input
          type="datetime-local"
        />

        <Input
          type="datetime-local"
        />

      </div>

    </div>
  );
}