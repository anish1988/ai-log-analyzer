import { Input } from "@/components/ui/input";

export default function SearchFields() {
  return (
    <div className="grid grid-cols-2 gap-6">

      <Input placeholder="Lead ID" />

      <Input placeholder="Campaign ID" />

      <Input placeholder="Caller Number" />

      <Input placeholder="Agent/User" />

    </div>
  );
}