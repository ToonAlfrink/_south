var whitelist = [
    "allergy",
    "anesthesiology",
    "audiology",
    "biology",
    "cardiology",
    "dermatology",
    "electrophysiology",
    "embryology",
    "endocrinology",
    "epidemiology",
    "gastroenterology",
    "gynaecology",
    "gynecology",
    "haematology",
    "hematology",
    "hepatology",
    "histology",
    "immunology",
    "microbiology",
    "neonatology",
    "nephrology",
    "neurology",
    "oncology",
    "ophthalmology",
    "otolaryngology",
    "otorhinolaryngology",
    "parasitology",
    "pathology",
    "perinatology",
    "pharmacology",
    "physiology",
    "psychology",
    "pulmonology",
    "radiology",
    "rheumatology",
    "toxicology",
    "traumatology",
    "urogynecology",
    "urology",
    "venereology"
 ]

var input = document.querySelector('input[name=tags]'),
    tagify = new Tagify(input, {
        pattern: /^.{0,20}$/,  // Validate typed tag(s) by Regex. Here maximum chars length is defined as "20"
        delimiters: ",| ",        // add new tags when a comma or a space character is entered
        keepInvalidTags: true,         // do not remove invalid tags (but keep them marked as invalid)
        editTags: 1,            // single click to edit a tag
        maxTags: 6,
        blacklist: ["foo", "bar", "baz"],
        whitelist: whitelist,
        transformTag: transformTag,
        backspace: "edit",
        placeholder: "Type something",
        dropdown : {
            enabled: 1,            // show suggestion after 1 typed character
            fuzzySearch: false,    // match only suggestions that starts with the typed characters
            position: 'text',      // position suggestions list next to typed text
            caseSensitive: true,   // allow adding duplicate items if their case is different
        },
        templates: {
            dropdownItemNoMatch: function(data) {
                return `<div class='${this.settings.classNames.dropdownItem}' tabindex="0" role="option">
                    No suggestion found for: <strong>${data.value}</strong>
                </div>`
            }
        }
    })

// generate a random color (in HSL format, which I like to use)
function getRandomColor(){
    function rand(min, max) {
        return min + Math.random() * (max - min);
    }

    var h = rand(1, 360)|0,
        s = rand(40, 70)|0,
        l = rand(65, 72)|0;

    return 'hsl(' + h + ',' + s + '%,' + l + '%)';
}

function transformTag( tagData ){
    tagData.style = "--tag-bg:" + getRandomColor();

    if( tagData.value.toLowerCase() == 'shit' )
       tagData.value = 's✲✲t'
}

tagify.on('add', function(e){
    console.log(e.detail)
})

tagify.on('invalid', function(e){
    console.log(e, e.detail);
})

var input = document.querySelector('input[name=tags-outside]')
// init Tagify script on the above inputs
var tagify = new Tagify(input, {
  whitelist: ["foo", "bar", "baz"],
  dropdown: {
    position: "input",
    enabled : 0 // always opens dropdown when input gets focus
  }
})