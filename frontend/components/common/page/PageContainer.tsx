import { ReactNode } from "react";

interface Props{
    children:ReactNode;
}

export default function PageContainer({
    children
}:Props){

    return(

        <div
            className="
            mx-auto
            max-w-[1450px]
            p-10
            "
        >

            {children}

        </div>

    );

}