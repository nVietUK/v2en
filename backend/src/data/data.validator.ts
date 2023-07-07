import { Injectable } from '@nestjs/common';
import {
	registerDecorator,
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
} from 'class-validator';

export function IsDataExistedByHashValue(validationOptions?: ValidationOptions) {
	return function (object: any, propertyName: string) {
		registerDecorator({
			name: 'isDataExisted',
			target: object.constructor,
			propertyName,
			options: validationOptions,
			validator: IsDataExistedByHashValueConstraint,
		});
	};
}

@Injectable()
@ValidatorConstraint({ async: true })
export class IsDataExistedByHashValueConstraint implements ValidatorConstraintInterface {
	constructor(private readonly connection: any) {}

	async validate(value: any): Promise<boolean> {
		return await this.createQueryBuilder(value);
	}

	private createQueryBuilder(value: any) {
		// return !this.connection.manager.findOneBy(Data, { hashValue: value });
		return true;
	}
}
