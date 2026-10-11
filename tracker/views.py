from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Sum, Q
from django.core.paginator import Paginator

from .models import Transaction
from .forms import TransactionForm, RegisterForm


# -----------------------------------
# USER REGISTRATION
# -----------------------------------

def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Account created successfully!"
            )

            return redirect("home")

    else:
        form = RegisterForm()

    return render(request, "register.html", {
        "form": form
    })


# -----------------------------------
# USER LOGIN
# -----------------------------------

def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(
                request,
                "Logged in successfully!"
            )

            return redirect("home")

    else:
        form = AuthenticationForm(request)

    return render(request, "login.html", {
        "form": form
    })


# -----------------------------------
# USER LOGOUT
# -----------------------------------

@login_required
@require_POST
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully!"
    )

    return redirect("login")


# -----------------------------------
# HOME DASHBOARD
# -----------------------------------

@login_required
def home(request):

    # ADD TRANSACTION
    if request.method == "POST":

        form = TransactionForm(request.POST)

        if form.is_valid():

            transaction = form.save(commit=False)

            transaction.user = request.user

            transaction.save()

            messages.success(
                request,
                "Transaction added successfully!"
            )

            return redirect("home")

    else:
        form = TransactionForm()

    # USER-SPECIFIC TRANSACTIONS
    transactions_list = Transaction.objects.filter(
        user=request.user
    )

    # -----------------------------------
    # SEARCH AND FILTER
    # -----------------------------------

    search_query = request.GET.get(
        "search", ""
    ).strip()

    transaction_type = request.GET.get(
        "type", ""
    ).strip()

    # -----------------------------------
    # NEW: MONTHLY FILTER
    # -----------------------------------

    selected_month = request.GET.get(
        "month", ""
    ).strip()

    if selected_month:

        try:
            year, month = map(
                int,
                selected_month.split("-")
            )

            if 1 <= year <= 9999 and 1 <= month <= 12:

                transactions_list = transactions_list.filter(
                    date__year=year,
                    date__month=month
                )

            else:
                selected_month = ""

        except (ValueError, OverflowError):
            selected_month = ""

    # -----------------------------------
    # SEARCH BY DESCRIPTION OR CATEGORY
    # -----------------------------------

    if search_query:

        transactions_list = transactions_list.filter(
            Q(description__icontains=search_query)
            | Q(category__icontains=search_query)
        )

    # -----------------------------------
    # FILTER BY TRANSACTION TYPE
    # -----------------------------------

    if transaction_type in ["Income", "Expense"]:

        transactions_list = transactions_list.filter(
            type=transaction_type
        )

    else:
        transaction_type = ""

    # -----------------------------------
    # SORT TRANSACTIONS
    # -----------------------------------

    transactions_list = transactions_list.order_by(
        "-date",
        "-id"
    )

    # -----------------------------------
    # PAGINATION
    # -----------------------------------

    paginator = Paginator(
        transactions_list,
        10
    )

    transactions = paginator.get_page(
        request.GET.get("page")
    )

    # -----------------------------------
    # TOTAL INCOME
    # -----------------------------------

    total_income = (
        Transaction.objects.filter(
            user=request.user,
            type="Income"
        ).aggregate(
            Sum("amount")
        )["amount__sum"] or 0
    )

    # -----------------------------------
    # TOTAL EXPENSES
    # -----------------------------------

    total_expenses = (
        Transaction.objects.filter(
            user=request.user,
            type="Expense"
        ).aggregate(
            Sum("amount")
        )["amount__sum"] or 0
    )

    # -----------------------------------
    # BALANCE
    # -----------------------------------

    balance = total_income - total_expenses

    # -----------------------------------
    # CHART 1: INCOME VS EXPENSES
    # -----------------------------------

    income_expense_data = [
        float(total_income),
        float(total_expenses)
    ]

    # -----------------------------------
    # CHART 2: EXPENSES BY CATEGORY
    # -----------------------------------

    category_data = (
        Transaction.objects
        .filter(
            user=request.user,
            type="Expense"
        )
        .values("category")
        .annotate(
            total=Sum("amount")
        )
        .order_by("category")
    )

    expense_categories = [
        item["category"]
        for item in category_data
    ]

    expense_amounts = [
        float(item["total"])
        for item in category_data
    ]

    # -----------------------------------
    # SEND DATA TO TEMPLATE
    # -----------------------------------

    context = {
        "form": form,
        "transactions": transactions,

        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,

        "search_query": search_query,
        "transaction_type": transaction_type,

        # NEW: Selected month
        "selected_month": selected_month,

        # Chart data
        "income_expense_data": income_expense_data,
        "expense_categories": expense_categories,
        "expense_amounts": expense_amounts,
    }

    return render(
        request,
        "home.html",
        context
    )


# -----------------------------------
# DELETE TRANSACTION
# -----------------------------------

@login_required
@require_POST
def delete_transaction(request, id):

    transaction = get_object_or_404(
        Transaction,
        id=id,
        user=request.user
    )

    transaction.delete()

    messages.success(
        request,
        "Transaction deleted successfully!"
    )

    return redirect("home")


# -----------------------------------
# EDIT TRANSACTION
# -----------------------------------

@login_required
def edit_transaction(request, id):

    transaction = get_object_or_404(
        Transaction,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        form = TransactionForm(
            request.POST,
            instance=transaction
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Transaction updated successfully!"
            )

            return redirect("home")

    else:
        form = TransactionForm(
            instance=transaction
        )

    return render(
        request,
        "edit.html",
        {
            "form": form,
            "transaction": transaction
        }
    )