from .forms import FeedbackForm


def feedback_form(request):
    """Make an empty FeedbackForm available in every template context."""
    return {'feedback_form': FeedbackForm()}
