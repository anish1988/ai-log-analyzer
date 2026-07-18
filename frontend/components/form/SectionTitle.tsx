import { ReactNode } from "react";

interface Props{

    title:string;

    icon:ReactNode;

}

export default function SectionTitle({

    title,

    icon

}:Props){

    return(

        <div
            className="
            mb-8
            flex
            items-center
            gap-3
            "
        >

            <div
                className="
                rounded-xl
                bg-indigo-50
                p-2
                "
            >

                {icon}

            </div>

            <h2
                className="
                text-xl
                font-semibold
                "
            >
                {title}
            </h2>

        </div>

    );

}