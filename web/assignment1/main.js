const heightRange = document.getElementById('id_height_range');
const heightNumber = document.getElementById('id_height_number');

heightRange.addEventListener('input', () => {
    heightNumber.value = heightRange.value;
});

heightNumber.addEventListener('input', () => {
    heightRange.value = heightNumber.value;
});

const yourName = document.getElementById('id_name');
const password = document.getElementById('id_password');
const password2 = document.getElementById('id_password2');
const gender = document.getElementsByName('name_gender');
const hobby = document.getElementsByName('name_hobby');
const birthday = document.getElementById('id_birth_date');
const color = document.getElementById('id_color');
const country = document.getElementById('id_country');
const profession = document.getElementById('id_profession');
const message = document.getElementById('id_message');




let s = ""
let extra = ""
function Validate() {
    let flag = true;
    extra = "";
    if (!yourName.value) flag = false;
    if (!password.value) flag = false;
    if (password.value.length > 20) flag = false;
    if (password.value.length < 8) flag = false;

    if (!password2.value) flag = false;
    if (password2.value.length > 20) flag = false;
    if (password2.value.length < 8) flag = false;
    if (password.value != password2.value) {
        extra += "Passwords do not match! "
        flag = false;
    };
    if (!birthday.value) flag = false;
    if (!profession.value) flag = false;

    return flag;

}

document.getElementById('id_button').addEventListener('click', () => {
    if (Validate()) {

        let genderSelected = "";
        for (let i = 0; i < gender.length; i++) {
            if (gender[i].checked) {
                genderSelected = gender[i].value;
            };
        };

        let hobbies = "";
        for (let i = 0; i < hobby.length; i++) {
            if (hobby[i].checked) {
                hobbies += hobby[i].value.toString() + ", ";
            }
        }

        s += "Your name: " + yourName.value + "<br>";
        if (password.value === password2.value) {
            s += "Your password: " + password.value + "<br>";
        }
        else {
            s += "Passwords do not match" + "<br>";
        };
        s += "Your gender: " + genderSelected + "<br>";
        s += "Your hobbies: " + hobbies + "<br>";
        s += "Your birthday: " + birthday.value + "<br>";
        s += "Your height: " + heightNumber.value + "<br>";
        s += "Your favourite color: <span style='color: " + color.value + ";'>" + color.value + "</span><br>";
        s += "Your home country: " + country.value + "<br>";
        s += "Your profession: " + profession.value + "<br><br>";
        s += "Your message: <br>" + message.value;


        const outputField = document.getElementById('id_output');
        outputField.innerHTML = s;
        s = "";
        genderSelected = "";
    }

    else {
        alert("Please fill in all required fields. " + extra);
        return;
    };




})



