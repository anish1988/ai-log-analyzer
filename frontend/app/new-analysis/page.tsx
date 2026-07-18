import PageContainer from "@/components/common/page/PageContainer";

import Stepper from "@/components/stepper/Stepper";

import SearchFilterCard from "@/components/analysis/search-filter-card/SearchFilterCard";

export default function NewAnalysisPage(){

    return(

        <PageContainer>

            <Stepper
                currentStep={1}
            />

            <div className="mt-8">

                <SearchFilterCard/>

            </div>

        </PageContainer>

    );

}