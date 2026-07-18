interface Props{
    label:string;
    required?:boolean;
}

export default function FormLabel({
    label,
    required
}:Props){

    return(

        <label
            className="
            mb-2.5
            block
            text-sm
            font-medium
            text-slate-800
            "
        >

            {label}

            {required && (

                <span
                    className="
                    ml-1
                    text-red-500
                    "
                >
                    *
                </span>

            )}

        </label>

    );

}