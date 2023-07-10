import {
	ValidationArguments,
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
	registerDecorator,
} from 'class-validator';
import { UserService } from './user.service';
import { Inject, Injectable, forwardRef } from '@nestjs/common';

export function IsUserNameExisted(validationOptions?: ValidationOptions) {
	return function (object: any, propertyName: string) {
		registerDecorator({
			target: object.constructor,
			propertyName,
			options: validationOptions,
			validator: IsUserNameExistedConstraint,
		});
	};
}

@ValidatorConstraint({ async: true })
@Injectable()
export class IsUserNameExistedConstraint
	implements ValidatorConstraintInterface
{
	constructor(
		@Inject(forwardRef(() => UserService))
		private readonly userService: UserService,
	) {}

	async validate(value: any): Promise<boolean> {
		return (await this.userService.findOneBy({ username: value })) == null;
	}
}
