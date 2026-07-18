"use client";

import { useState } from "react";

import ChipSelector from "@/components/form/ChipSelector";

import { tierOptions } from "@/config/tier-options";

export default function TierSection() {
  const [selectedTier, setSelectedTier] = useState("all");

  return (
    <ChipSelector
      label="Tier"
      value={selectedTier}
      options={tierOptions}
      onChange={setSelectedTier}
    />
  );
}