<?php

class Home extends TPage
{
	public function sendScript($sender, $param)
	{
		$this->Script1->render($param->NewWriter);
	}
}
