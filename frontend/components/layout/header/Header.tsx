import PageTitle from "./components/PageTitle";
import HeaderActions from "./components/HeaderActions";

export default function Header() {
  return (
    <header className="flex h-20 items-center justify-between border-b bg-white px-8">
      <PageTitle
        title="New Log Analysis"
        description="Analyze and troubleshoot log files"
      />

      <HeaderActions />
    </header>
  );
}