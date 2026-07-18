import FormLabel from "./FormLabel";

interface Props{

    label:string;

    placeholder:string;

    required?:boolean;

}

export default function TextField({

    label,

    placeholder,

    required

}:Props){

    return(

        <div>

            <FormLabel

                label={label}

                required={required}

            />

            <input

                placeholder={placeholder}

                className="
                h-12
                w-full
                rounded-xl
                border
                border-slate-300
                bg-white
                px-4
                text-[15px]
                outline-none
                transition

                focus:border-indigo-500

                focus:ring-2

                focus:ring-indigo-100
                "

            />

        </div>

    );

}