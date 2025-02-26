"""test_check_labels.py"""

from typing import Any, List
from unittest import TestCase, mock, main

from check_labels import (
    main as check_labels_main,
    add_label_err_comment,
    delete_all_label_err_comments,
)
from github_utils import GitHubComment
from label_utils import BOT_AUTHORS, LABEL_ERR_MSG_TITLE
from test_trymerge import mocked_gh_graphql, mock_gh_get_info
from trymerge import GitHubPR

def mock_parse_args() -> object:
    class Object(object):
        def __init__(self) -> None:
            self.pr_num = 76123
    return Object()

def mock_add_label_err_comment(pr: "GitHubPR") -> None:
    pass

def mock_delete_all_label_err_comments(pr: "GitHubPR") -> None:
    pass

def mock_get_comments() -> List[GitHubComment]:
    return [
        # Case 1 - a non label err comment
        GitHubComment(
            body_text="mock_body_text",
            created_at="",
            author_login="",
            author_association="",
            editor_login=None,
            database_id=1,
        ),
        # Case 2 - a label err comment
        GitHubComment(
            body_text=" #" + LABEL_ERR_MSG_TITLE,
            created_at="",
            author_login=BOT_AUTHORS[1],
            author_association="",
            editor_login=None,
            database_id=2,
        ),
    ]


class TestCheckLabels(TestCase):
    @mock.patch('trymerge.gh_graphql', side_effect=mocked_gh_graphql)
    @mock.patch('trymerge.GitHubPR.get_comments', return_value=[mock_get_comments()[0]])
    @mock.patch('check_labels.gh_post_pr_comment')
    def test_correctly_add_label_err_comment(
        self, mock_gh_post_pr_comment: Any, mock_get_comments: Any, mock_gh_grphql: Any
    ) -> None:
        "Test add label err comment when similar comments don't exist."
        pr = GitHubPR("pytorch", "pytorch", 75095)
        add_label_err_comment(pr)
        mock_gh_post_pr_comment.assert_called_once()

    @mock.patch('trymerge.gh_graphql', side_effect=mocked_gh_graphql)
    @mock.patch('trymerge.GitHubPR.get_comments', return_value=[mock_get_comments()[1]])
    @mock.patch('check_labels.gh_post_pr_comment')
    def test_not_add_label_err_comment(
        self, mock_gh_post_pr_comment: Any, mock_get_comments: Any, mock_gh_grphql: Any
    ) -> None:
        "Test not add label err comment when similar comments exist."
        pr = GitHubPR("pytorch", "pytorch", 75095)
        add_label_err_comment(pr)
        mock_gh_post_pr_comment.assert_not_called()

    @mock.patch('trymerge.gh_graphql', side_effect=mocked_gh_graphql)
    @mock.patch('trymerge.GitHubPR.get_comments', return_value=mock_get_comments())
    @mock.patch('check_labels.gh_delete_comment')
    def test_correctly_delete_all_label_err_comments(
        self, mock_gh_delete_comment: Any, mock_get_comments: Any, mock_gh_grphql: Any
    ) -> None:
        "Test only delete label err comment."
        pr = GitHubPR("pytorch", "pytorch", 75095)
        delete_all_label_err_comments(pr)
        mock_gh_delete_comment.assert_called_once_with("pytorch", "pytorch", 2)

    @mock.patch('trymerge.gh_get_pr_info', return_value=mock_gh_get_info())
    @mock.patch('check_labels.parse_args', return_value=mock_parse_args())
    @mock.patch('check_labels.has_required_labels', return_value=False)
    @mock.patch('check_labels.delete_all_label_err_comments', side_effect=mock_delete_all_label_err_comments)
    @mock.patch('check_labels.add_label_err_comment', side_effect=mock_add_label_err_comment)
    def test_ci_fails_without_required_labels(
        self,
        mock_add_label_err_comment: Any,
        mock_delete_all_label_err_comments: Any,
        mock_has_required_labels: Any,
        mock_parse_args: Any,
        mock_gh_get_info: Any,
    ) -> None:
        with self.assertRaises(SystemExit) as sys_exit:
            check_labels_main()
        self.assertEqual(str(sys_exit.exception), "1")
        mock_add_label_err_comment.assert_called_once()
        mock_delete_all_label_err_comments.assert_not_called()

    @mock.patch('trymerge.gh_get_pr_info', return_value=mock_gh_get_info())
    @mock.patch('check_labels.parse_args', return_value=mock_parse_args())
    @mock.patch('check_labels.has_required_labels', return_value=True)
    @mock.patch('check_labels.delete_all_label_err_comments', side_effect=mock_delete_all_label_err_comments)
    @mock.patch('check_labels.add_label_err_comment', side_effect=mock_add_label_err_comment)
    def test_ci_success_with_required_labels(
        self,
        mock_add_label_err_comment: Any,
        mock_delete_all_label_err_comments: Any,
        mock_has_required_labels: Any,
        mock_parse_args: Any,
        mock_gh_get_info: Any,
    ) -> None:
        with self.assertRaises(SystemExit) as sys_exit:
            check_labels_main()
        self.assertEqual(str(sys_exit.exception), "0")
        mock_add_label_err_comment.assert_not_called()
        mock_delete_all_label_err_comments.assert_called_once()

if __name__ == "__main__":
    main()
