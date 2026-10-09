const fromCurrency = document.getElementById("from_currency");
const toCurrency = document.getElementById("to_currency");
const sourceSelect = document.getElementById("source");
const rateTypeGroup = document.getElementById("rate-type-group");
const rateTypeSelect = document.getElementById("rate_type");
const convertButton = document.getElementById("convert-btn");
const swapButton = document.getElementById("swap-btn");
const currencyNotice = document.getElementById("currency-notice");

const currencyData = JSON.parse(
    document.getElementById("currency-data").textContent
);

let selectedBuyType =
    rateTypeSelect.dataset.selected === "cash" ? "cash" : "transfer";


// Tạo lại dropdown chỉ với các đồng tiền hợp lệ.
// Giữ lựa chọn hiện tại nếu vẫn được hỗ trợ.
function fillCurrencies(select, currencies, preferredValue) {
    select.replaceChildren();

    for (const currency of currencies) {
        select.add(new Option(
            currency.iso_code + " - " + currency.name,
            currency.iso_code
        ));
    }

    if (currencies.some(item => item.iso_code === preferredValue)) {
        select.value = preferredValue;
    } else {
        select.value = currencies.length ? currencies[0].iso_code : "";
    }

    select.disabled = currencies.length === 0;
}


function updateForm(
    preferredFrom = fromCurrency.value,
    preferredTo = toCurrency.value
) {
    const isVcb = sourceSelect.value === "vietcombank";

    rateTypeGroup.style.display = isVcb ? "flex" : "none";
    rateTypeSelect.disabled = !isVcb;
    rateTypeSelect.replaceChildren();

    if (!isVcb) {
        // Frankfurter dùng danh sách riêng của Frankfurter.
        fillCurrencies(
            fromCurrency,
            currencyData.frankfurter,
            preferredFrom
        );

        fillCurrencies(
            toCurrency,
            currencyData.frankfurter,
            preferredTo
        );

        currencyNotice.textContent = currencyData.frankfurter.length
            ? ""
            : "Không tải được danh sách tiền tệ Frankfurter.";
    } else {
        const foreignCurrencies = currencyData.vietcombank;

        // cash: phải có giá mua tiền mặt.
        // transfer: phải có giá mua chuyển khoản.
        const buyCurrencies = foreignCurrencies.filter(
            item => item[selectedBuyType]
        );

        // Chiều VND -> ngoại tệ phải có giá bán.
        const sellCurrencies = foreignCurrencies.filter(
            item => item.sell
        );

        const vnd = {
            iso_code: "VND",
            name: "Vietnamese Dong"
        };

        const fromOptions = [...buyCurrencies];

        // Chỉ cho chọn VND làm tiền nguồn
        // khi có ít nhất một ngoại tệ có giá bán.
        if (sellCurrencies.length) {
            fromOptions.push(vnd);
        }

        fillCurrencies(
            fromCurrency,
            fromOptions,
            preferredFrom
        );

        if (fromCurrency.value === "VND") {
            // VND -> ngoại tệ: chỉ hiện tiền có giá bán.
            fillCurrencies(
                toCurrency,
                sellCurrencies,
                preferredTo
            );

            rateTypeSelect.add(
                new Option("Bán (Sell)", "sell")
            );

            rateTypeSelect.value = "sell";
        } else {
            // Ngoại tệ -> VND.
            fillCurrencies(
                toCurrency,
                buyCurrencies.length ? [vnd] : [],
                "VND"
            );

            rateTypeSelect.add(
                new Option("Mua chuyển khoản", "transfer")
            );

            rateTypeSelect.add(
                new Option("Mua tiền mặt", "cash")
            );

            rateTypeSelect.value = selectedBuyType;
        }

        currencyNotice.textContent = foreignCurrencies.length
            ? "Chỉ hiển thị ngoại tệ có tỷ giá cho loại giao dịch đang chọn."
            : "Không tải được tỷ giá Vietcombank. Bạn hãy tải lại trang hoặc chọn Frankfurter.";
    }

    const canConvert = Boolean(
        fromCurrency.value && toCurrency.value
    );

    convertButton.disabled = !canConvert;
    swapButton.disabled = !canConvert;
}


// Đổi loại mua -> lọc lại ngay danh sách ngoại tệ.
rateTypeSelect.addEventListener("change", function () {
    if (this.value === "cash" || this.value === "transfer") {
        selectedBuyType = this.value;
    }

    updateForm();
});


// Đổi nguồn hoặc tiền tệ -> cập nhật danh sách và loại giao dịch.
sourceSelect.addEventListener("change", () => updateForm());
fromCurrency.addEventListener("change", () => updateForm());
toCurrency.addEventListener("change", () => updateForm());


// Đổi chiều và giữ cặp tiền nếu chiều mới có tỷ giá phù hợp.
swapButton.addEventListener("click", function () {
    updateForm(toCurrency.value, fromCurrency.value);
});


// Khôi phục form khi mở trang hoặc sau khi chuyển đổi.
updateForm();