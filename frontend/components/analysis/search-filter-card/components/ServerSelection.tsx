import { Input } from "@/components/ui/input";

export default function ServerSelection() {
  return (
    <div>

      <h3 className="mb-4 text-lg font-semibold">
        Servers
      </h3>

      <Input
        placeholder="Select servers..."
      />

    </div>
  );
}