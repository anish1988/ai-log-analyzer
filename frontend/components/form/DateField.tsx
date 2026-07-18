import FormLabel from "./FormLabel";

interface Props{

    label:string;

}

export default function DateField({

    label

}:Props){

    return(

        <div>

            <FormLabel
                label={label}
                required
            />

            <input

                type="datetime-local"

                className="
                h-12
                w-full
                rounded-xl
                border
                border-slate-300
                px-4
                "

            />

        </div>

    );

}